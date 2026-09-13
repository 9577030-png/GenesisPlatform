from __future__ import annotations

from genesis_medical.domain.entities.finding import ClinicalFinding
from genesis_medical.domain.entities.parameter import Parameter
from genesis_medical.domain.entities.patient import PatientProfile
from genesis_medical.domain.entities.report import AnalysisReport
from genesis_medical.services import ActionMapper, ReportBuilder

from .inference_engine import InferenceEngine


class MedicalAnalysisService:
    """Orchestrate the medical analysis workflow."""

    def __init__(
        self,
        inference_engine: InferenceEngine,
        action_mapper: ActionMapper,
        report_builder: ReportBuilder,
    ) -> None:
        self.inference_engine = inference_engine
        self.action_mapper = action_mapper
        self.report_builder = report_builder

    def analyze(
        self,
        patient: PatientProfile,
        parameters: list[Parameter],
    ) -> AnalysisReport:
        findings: list[ClinicalFinding] = self.inference_engine.infer(
            patient,
            parameters,
        )
        actions = self.action_mapper.map_to_actions(findings)
        return self.report_builder.build(findings, actions)
