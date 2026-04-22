"""
DevOps Agent — Task Database Model
"""

from sqlalchemy import Column, String, Text, Float, Integer, Boolean, DateTime
from sqlalchemy.sql import func
from api.models.database import Base


class TaskModel(Base):
    __tablename__ = "tasks"

    id = Column(String(12), primary_key=True)
    task = Column(Text, nullable=False)
    status = Column(String(20), default="pending")
    priority = Column(String(10), default="medium")
    result = Column(Text, nullable=True)
    trace = Column(Text, nullable=True)  # JSON string
    tools_used = Column(String(500), nullable=True)
    iterations = Column(Integer, default=0)
    duration_seconds = Column(Float, nullable=True)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
