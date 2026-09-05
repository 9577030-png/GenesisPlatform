from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from typing import Dict, Any
from medical_app.infrastructure.repositories.sqlalchemy_models import Base, AuditLogModel

class AuditRepository:
    def __init__(self, db_url: str):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def log(self, patient_id: str, user_id: int, request_data: Dict, result_summary: Dict, rules_version: str) -> None:
        with self.Session() as session:
            log = AuditLogModel(
                patient_id=patient_id,
                user_id=user_id,
                request_data=request_data,
                result_summary=result_summary,
                rules_version=rules_version
            )
            session.add(log)
            session.commit()
