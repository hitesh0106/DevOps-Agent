
from pipelines.stage import PipelineStage
from pipelines.pipeline_engine import Pipeline


def create_node_ci_pipeline(repo: str = "frontend-app") -> Pipeline:
    """Pre-built Node.js CI pipeline."""
    pipeline = Pipeline(name="Node CI", repo=repo, trigger="push")
    pipeline.add_stage(PipelineStage(name="checkout", command="git checkout", description="Checkout source code"))
    pipeline.add_stage(PipelineStage(name="install", command="npm ci", description="Install dependencies"))
    pipeline.add_stage(PipelineStage(name="lint", command="npm run lint", description="ESLint check", allow_failure=True))
    pipeline.add_stage(PipelineStage(name="test", command="npm test", description="Run tests"))
    pipeline.add_stage(PipelineStage(name="build", command="npm run build", description="Production build"))
    return pipeline
