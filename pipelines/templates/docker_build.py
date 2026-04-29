
from pipelines.stage import PipelineStage
from pipelines.pipeline_engine import Pipeline


def create_docker_build_pipeline(repo: str = "main-app") -> Pipeline:
    """Pre-built Docker build and push pipeline."""
    pipeline = Pipeline(name="Docker Build", repo=repo, trigger="merge")
    pipeline.add_stage(PipelineStage(name="checkout", command="git checkout", description="Checkout source"))
    pipeline.add_stage(PipelineStage(name="build", command="docker build -t app:latest .", description="Build Docker image"))
    pipeline.add_stage(PipelineStage(name="scan", command="trivy image app:latest", description="Security scan", allow_failure=True))
    pipeline.add_stage(PipelineStage(name="push", command="docker push app:latest", description="Push to registry"))
    return pipeline
