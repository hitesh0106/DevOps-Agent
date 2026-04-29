
from pipelines.stage import PipelineStage
from pipelines.pipeline_engine import Pipeline


def create_k8s_deploy_pipeline(repo: str = "main-app") -> Pipeline:
    """Pre-built Kubernetes deployment pipeline."""
    pipeline = Pipeline(name="K8s Deploy", repo=repo, trigger="manual")
    pipeline.add_stage(PipelineStage(name="validate", command="kubectl apply --dry-run=client -f k8s/", description="Validate manifests"))
    pipeline.add_stage(PipelineStage(name="deploy", command="kubectl apply -f k8s/", description="Apply manifests"))
    pipeline.add_stage(PipelineStage(name="rollout", command="kubectl rollout status deployment/app", description="Wait for rollout"))
    pipeline.add_stage(PipelineStage(name="healthcheck", command="curl -f http://app:8080/health", description="Post-deploy health check"))
    return pipeline
