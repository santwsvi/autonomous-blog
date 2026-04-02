import { NextRequest, NextResponse } from "next/server";
import { revalidatePath } from "next/cache";
import { createHmac, timingSafeEqual } from "crypto";

export async function POST(request: NextRequest) {
  const signature = request.headers.get("x-revalidation-signature");
  if (!signature) {
    return NextResponse.json({ error: "Missing signature" }, { status: 401 });
  }

  const secret = process.env.REVALIDATION_SECRET;
  if (!secret) {
    return NextResponse.json(
      { error: "Server misconfigured" },
      { status: 500 }
    );
  }

  const body = await request.text();
  const expected = createHmac("sha256", secret).update(body).digest("hex");

  try {
    const sigBuffer = Buffer.from(signature, "utf-8");
    const expectedBuffer = Buffer.from(expected, "utf-8");

    if (
      sigBuffer.length !== expectedBuffer.length ||
      !timingSafeEqual(sigBuffer, expectedBuffer)
    ) {
      return NextResponse.json(
        { error: "Invalid signature" },
        { status: 401 }
      );
    }
  } catch {
    return NextResponse.json({ error: "Invalid signature" }, { status: 401 });
  }

  // Revalidate blog pages
  revalidatePath("/", "layout");

  try {
    const payload = JSON.parse(body);
    if (payload.slug) {
      revalidatePath(`/${payload.slug}`, "page");
    }
  } catch {
    // Body might not be JSON — still revalidate root
  }

  return NextResponse.json({ revalidated: true });
}
