"""
DevOps Agent — Agent Task Worker
"""

from workers.celery_app import celery_app
from config.logging_config import get_logger

logger = get_logger(__name__)


@celery_app.task(name="workers.agent_worker.run_agent_task", bind=True, max_retries=2)
def run_agent_task(self, task: str, priority: str = "medium", context: dict = None):
    """Execute a DevOps agent task asynchronously."""
    logger.info("Agent worker processing task", task=task[:80])
    try:
        from agent.core import DevOpsAgent
        from config.constants import TaskPriority
        agent = DevOpsAgent()
        result = agent.run(task=task, priority=TaskPriority(priority), context=context)
        return result
    except Exception as exc:
        logger.error("Agent task failed", error=str(exc))
        raise self.retry(exc=exc, countdown=30)
