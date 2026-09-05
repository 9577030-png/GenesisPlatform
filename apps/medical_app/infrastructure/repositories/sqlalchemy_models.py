from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON, Enum
from sqlalchemy.orm import declarative_base
from datetime import datetime, UTC
from genesis_medical.domain.rule_version import RulePriority, RuleTier

Base = declarative_base()

class RuleVersionModel(Base):
    __tablename__ = "rule_versions"
    version_id = Column(Integer, primary_key=True, autoincrement=True)
    rule_id = Column(String(100), index=True)
    name = Column(String(255))
    conditions = Column(JSON)
    actions = Column(JSON)
    priority = Column(Enum(RulePriority))
    conflicts_with = Column(JSON)
    supports = Column(JSON)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    created_by = Column(String(100))
    is_active = Column(Boolean, default=False)
    comment = Column(String(500), nullable=True)
    tier = Column(Enum(RuleTier), default=RuleTier.BASIC)

class AuditLogModel(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(String(100))
    user_id = Column(Integer)
    request_data = Column(JSON)
    result_summary = Column(JSON)
    rules_version = Column(String(50))
    timestamp = Column(DateTime, default=lambda: datetime.now(UTC))
