
from pipelines.stage import PipelineStage
from pipelines.pipeline_engine import Pipeline


def create_python_ci_pipeline(repo: str = "backend-api") -> Pipeline:
    """Pre-built Python CI pipeline."""
    pipeline = Pipeline(name="Python CI", repo=repo, trigger="push")
    pipeline.add_stage(PipelineStage(name="checkout", command="git checkout", description="Checkout source code"))
    pipeline.add_stage(PipelineStage(name="install", command="pip install -r requirements.txt", description="Install dependencies"))
    pipeline.add_stage(PipelineStage(name="lint", command="flake8 .", description="Code linting", allow_failure=True))
    pipeline.add_stage(PipelineStage(name="test", command="pytest tests/ -v", description="Run unit tests"))
    pipeline.add_stage(PipelineStage(name="coverage", command="pytest --cov", description="Generate coverage report", allow_failure=True))
    return pipeline
