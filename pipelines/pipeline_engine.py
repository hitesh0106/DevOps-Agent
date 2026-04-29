
import time
import uuid
from typing import Optional
from config.logging_config import get_logger
from pipelines.stage import PipelineStage, StageStatus

logger = get_logger(__name__)


class Pipeline:
    """Represents a CI/CD pipeline with ordered stages."""

    def __init__(self, name: str, repo: str = "", trigger: str = "manual"):
        self.id = f"pipe-{str(uuid.uuid4())[:6]}"
        self.name = name
        self.repo = repo
        self.trigger = trigger
        self.stages: list[PipelineStage] = []
        self.status = "idle"
        self.run_count = 0

    def add_stage(self, stage: PipelineStage):
        self.stages.append(stage)

    def to_dict(self) -> dict:
        return {
            "id": self.id, "name": self.name, "repo": self.repo,
            "trigger": self.trigger, "status": self.status,
            "run_count": self.run_count,
            "stages": [s.to_dict() for s in self.stages],
        }


class PipelineEngine:
    """
    Executes CI/CD pipelines stage by stage.
    In simulation mode, generates realistic mock outputs.
    """

    def __init__(self, simulation_mode: bool = True):
        self.simulation_mode = simulation_mode
        self._pipelines: dict[str, Pipeline] = {}
        self._history: list[dict] = []

    def register(self, pipeline: Pipeline):
        self._pipelines[pipeline.id] = pipeline
        logger.info("Pipeline registered", id=pipeline.id, name=pipeline.name)

    def run(self, pipeline_id: str, branch: str = "main", params: dict = None) -> dict:
        """Execute a pipeline by ID."""
        pipeline = self._pipelines.get(pipeline_id)
        if not pipeline:
            return {"error": f"Pipeline {pipeline_id} not found"}

        pipeline.status = "running"
        pipeline.run_count += 1
        run_id = f"run-{str(uuid.uuid4())[:6]}"
        start = time.time()
        results = []

        for stage in pipeline.stages:
            stage.status = StageStatus.RUNNING
            stage_start = time.time()

            if self.simulation_mode:
                time.sleep(0.1)  # Simulate work
                stage.status = StageStatus.SUCCESS
                output = f"[sim] {stage.name} completed successfully"
            else:
                try:
                    output = stage.execute()
                    stage.status = StageStatus.SUCCESS
                except Exception as e:
                    stage.status = StageStatus.FAILED
                    output = str(e)
                    pipeline.status = "failed"
                    results.append({"stage": stage.name, "status": "failed", "output": output, "duration": f"{time.time()-stage_start:.1f}s"})
                    break

            results.append({
                "stage": stage.name, "status": stage.status.value,
                "output": output, "duration": f"{time.time()-stage_start:.1f}s",
            })

        if pipeline.status != "failed":
            pipeline.status = "success"

        run_result = {
            "run_id": run_id, "pipeline_id": pipeline_id,
            "pipeline_name": pipeline.name, "branch": branch,
            "status": pipeline.status, "stages": results,
            "total_duration": f"{time.time()-start:.1f}s",
        }
        self._history.append(run_result)
        return run_result

    def get_history(self, limit: int = 10) -> list[dict]:
        return self._history[-limit:]

    def list_pipelines(self) -> list[dict]:
        return [p.to_dict() for p in self._pipelines.values()]
