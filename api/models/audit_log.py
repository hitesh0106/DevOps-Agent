"""
DevOps Agent — Audit Log Database Model
"""

from sqlalchemy import Column, String, Text, Boolean, DateTime
from sqlalchemy.sql import func
from api.models.database import Base


class AuditLogModel(Base):
    __tablename__ = "audit_logs"

    id = Column(String(20), primary_key=True)
    agent_id = Column(String(10), nullable=True)
    action = Column(String(100), nullable=False)
    input_data = Column(Text, nullable=True)
    output_data = Column(Text, nullable=True)
    success = Column(Boolean, default=True)
    risk_level = Column(String(20), default="safe")
    reasoning = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
