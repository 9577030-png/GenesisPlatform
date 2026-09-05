import os
import sqlite3
import json
import logging
from typing import Optional
from enum import Enum
from dataclasses import asdict
from datetime import datetime
from genesis_medical.domain.entities.report import AnalysisReport
from genesis_medical.domain.entities.finding import ClinicalFinding
from genesis_medical.domain.entities.recommendation import Recommendation
from genesis_medical.domain.value_objects.risk_level import RiskLevel
from genesis_medical.domain.value_objects.severity import Severity
from medical_app.application.ports.history_repository import HistoryRepository

logger = logging.getLogger(__name__)

class SqlHistoryRepository(HistoryRepository):
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = os.getenv("DB_PATH", "history.db")
        self.db_path = db_path
        self._init_db()
        logger.info(f"SqlHistoryRepository initialized with database: {db_path}")

    def _init_db(self) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                report_json TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()
        logger.debug("Database table 'reports' ensured")

    def _serialize_report(self, report: AnalysisReport) -> str:
        def enum_to_str(obj):
            if isinstance(obj, Enum):
                return obj.name
            return str(obj)

        data = {
            "findings": [
                {
                    "id": f.id,
                    "title": f.title,
                    "probability": f.probability,
                    "risk": f.risk.name,
                    "doctor_specialty": f.doctor_specialty,
                    "tests": f.tests,
                    "evidence": f.evidence,
                    "excluded_by": f.excluded_by
                }
                for f in report.findings
            ],
            "actions": [
                {
                    "doctor_specialty": a.doctor_specialty,
                    "urgency": a.urgency.name,
                    "additional_tests": a.additional_tests
                }
                for a in report.actions
            ],
            "explanation": report.explanation
        }
        return json.dumps(data, default=enum_to_str, ensure_ascii=False)

    def _deserialize_report(self, json_str: str) -> AnalysisReport:
        data = json.loads(json_str)
        findings = []
        for f_data in data["findings"]:
            risk_name = f_data.get("risk")
            try:
                risk = RiskLevel[risk_name] if risk_name in RiskLevel.__members__ else RiskLevel.NORMAL
            except (KeyError, ValueError):
                risk = RiskLevel.NORMAL
            finding = ClinicalFinding(
                id=f_data["id"],
                title=f_data["title"],
                probability=f_data["probability"],
                risk=risk,
                doctor_specialty=f_data.get("doctor_specialty"),
                tests=f_data.get("tests", []),
                evidence=f_data.get("evidence", []),
                excluded_by=f_data.get("excluded_by", [])
            )
            findings.append(finding)
        actions = []
        for a_data in data["actions"]:
            urgency_name = a_data.get("urgency")
            try:
                urgency = Severity[urgency_name] if urgency_name in Severity.__members__ else Severity.MODERATE
            except (KeyError, ValueError):
                urgency = Severity.MODERATE
            action = Recommendation(
                doctor_specialty=a_data["doctor_specialty"],
                urgency=urgency,
                additional_tests=a_data.get("additional_tests", [])
            )
            actions.append(action)
        return AnalysisReport(
            findings=findings,
            actions=actions,
            explanation=data.get("explanation", "")
        )

    def save(self, patient_id: str, report: AnalysisReport) -> None:
        logger.info(f"Saving report for patient {patient_id}")
        json_data = self._serialize_report(report)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO reports (patient_id, report_json) VALUES (?, ?)",
            (patient_id, json_data)
        )
        conn.commit()
        conn.close()
        logger.info(f"Report saved for patient {patient_id}")

    def load(self, patient_id: str) -> Optional[AnalysisReport]:
        logger.info(f"Loading last report for patient {patient_id}")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT report_json FROM reports WHERE patient_id = ? ORDER BY id DESC LIMIT 1",
            (patient_id,)
        )
        row = cursor.fetchone()
        conn.close()
        if row is None:
            logger.warning(f"No history found for patient {patient_id}")
            return None
        report = self._deserialize_report(row[0])
        logger.info(f"Loaded report for patient {patient_id}")
        return report
