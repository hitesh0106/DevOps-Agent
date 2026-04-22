"""
DevOps Agent — Incident Database Model
"""

from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.sql import func
from api.models.database import Base


class IncidentModel(Base):
    __tablename__ = "incidents"

    id = Column(String(20), primary_key=True)
    title = Column(String(200), nullable=False)
    severity = Column(String(20), default="info")
    status = Column(String(20), default="open")
    source = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    resolution = Column(Text, nullable=True)
    resolved_by = Column(String(50), nullable=True)
    duration = Column(String(20), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)
