"""Agent state definition for the content generation pipeline."""

from pydantic import BaseModel, Field


class QualityScores(BaseModel):
    readability: float = 0.0
    coherence: float = 0.0
    depth: float = 0.0
    originality: float = 0.0
    factual_accuracy: float = 0.0
    overall: float = 0.0


class AgentState(BaseModel):
    """State shared across all nodes in the generation graph."""

    model_config = {"extra": "ignore"}

    # Input
    topic: str = ""
    instructions: str = ""
    language: str = "pt-BR"

    # RAG context (injected before graph runs)
    rag_context: str = ""

    # Researcher output
    research_context: str = ""
    sources: list[str] = Field(default_factory=list)

    # Writer output
    draft: str = ""

    # Editor output
    feedback: str = ""
    quality_scores: QualityScores = Field(default_factory=QualityScores)
    approved: bool = False

    # SEO output
    seo_title: str = ""
    seo_description: str = ""
    seo_slug: str = ""
    seo_tags: list[str] = Field(default_factory=list)

    # Publisher output
    final_mdx: str = ""
    post_id: str = ""

    # Control
    iteration: int = 0
    max_iterations: int = 3
    errors: list[str] = Field(default_factory=list)

    # Tracking
    model_usage: dict = Field(default_factory=dict)
    prompt_versions: dict = Field(default_factory=dict)
