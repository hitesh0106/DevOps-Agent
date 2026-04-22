"""
DevOps Agent — Pipeline Database Model
"""

from sqlalchemy import Column, String, Text, Integer, DateTime
from sqlalchemy.sql import func
from api.models.database import Base


class PipelineModel(Base):
    __tablename__ = "pipelines"

    id = Column(String(20), primary_key=True)
    name = Column(String(100), nullable=False)
    repo = Column(String(200), nullable=True)
    status = Column(String(20), default="idle")
    trigger = Column(String(50), nullable=True)
    branch = Column(String(100), default="main")
    run_count = Column(Integer, default=0)
    last_run = Column(DateTime(timezone=True), nullable=True)
    last_duration = Column(String(20), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
