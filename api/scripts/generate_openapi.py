import json

from app.main import app


def main() -> None:
    spec = app.openapi()
    with open("openapi.json", "w") as f:
        json.dump(spec, f, indent=2)
    print("OpenAPI spec exported to openapi.json")


if __name__ == "__main__":
    main()
