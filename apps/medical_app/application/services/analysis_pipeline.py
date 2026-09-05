import logging
from typing import List, Dict, Any, Optional
from genesis_medical.domain.entities.patient import PatientProfile
from genesis_medical.domain.entities.parameter import Parameter
from genesis_medical.domain.entities.report import AnalysisReport
from genesis_medical.domain.entities.finding import ClinicalFinding          # <-- РґРѕР±Р°РІР»РµРЅРѕ
from genesis_medical.domain.entities.recommendation import Recommendation   # <-- РґРѕР±Р°РІР»РµРЅРѕ
from medical_app.application.ports.parser_interface import ParserInterface
from medical_app.application.ports.history_repository import HistoryRepository
from medical_app.application.ports.renderer_interface import RendererInterface
from medical_app.application.services.inference_engine import InferenceEngine
from genesis_medical.services import ActionMapper
from genesis_medical.services import ReportBuilder
from genesis_medical.services import PostProcessor
from genesis_medical.domain.exceptions import MedicalAIError
from medical_app.infrastructure.cache.redis_cache import RedisCache
from medical_app.infrastructure.repositories.audit_repository import AuditRepository
from medical_app.application.ports.rule_repository import RuleRepository
from genesis_medical.services import PhysiologicalValidator

logger = logging.getLogger(__name__)

class AnalysisPipeline:
    def __init__(
        self,
        parser: ParserInterface,
        inference_engine: InferenceEngine,
        action_mapper: ActionMapper,
        report_builder: ReportBuilder,
        history_repo: HistoryRepository,
        renderer: RendererInterface,
        post_processor: Optional[PostProcessor] = None,
        cache: Optional[RedisCache] = None,
        audit_repo: Optional[AuditRepository] = None,
        rule_repo: Optional[RuleRepository] = None,
        validator: Optional[PhysiologicalValidator] = None
    ):
        self.parser = parser
        self.inference_engine = inference_engine
        self.action_mapper = action_mapper
        self.report_builder = report_builder
        self.history_repo = history_repo
        self.renderer = renderer
        self.post_processor = post_processor or PostProcessor()
        self.cache = cache
        self.audit_repo = audit_repo
        self.rule_repo = rule_repo
        self.validator = validator

    def _get_rules_version(self) -> str:
        if self.rule_repo:
            active = self.rule_repo.get_active_versions()
            version_str = ",".join(f"{r.rule_id}:{r.version_id}" for r in sorted(active, key=lambda x: x.rule_id))
            import hashlib
            return hashlib.md5(version_str.encode()).hexdigest()
        return "unknown"

    def run_structured(self, patient: PatientProfile, raw_text: str, user_id: int = None) -> AnalysisReport:
        logger.info(f"Structured run for patient {patient.id}")
        try:
            # 1. Р’Р°Р»РёРґР°С†РёСЏ
            if self.validator:
                parameters = self.parser.parse(raw_text)
                errors = self.validator.validate([{"name": p.name, "value": p.value} for p in parameters])
                if errors:
                    raise MedicalAIError(f"Validation errors: {', '.join(errors)}")

            # 2. РљСЌС€ (СЃ РѕР±СЂР°Р±РѕС‚РєРѕР№ РѕС€РёР±РѕРє)
            if self.cache:
                try:
                    rules_version = self._get_rules_version()
                    parameters = self.parser.parse(raw_text)
                    cached_result = self.cache.get(patient, parameters, rules_version)
                    if cached_result:
                        logger.info("Cache hit for patient")
                        report = AnalysisReport(
                            findings=[ClinicalFinding(**f) for f in cached_result.get("findings", [])],
                            actions=[Recommendation(**a) for a in cached_result.get("actions", [])],
                            explanation=cached_result.get("explanation", "")
                        )
                        self.history_repo.save(patient.id, report)
                        if self.audit_repo and user_id:
                            self.audit_repo.log(
                                patient_id=patient.id,
                                user_id=user_id,
                                request_data={"raw_text": raw_text, "patient": patient},
                                result_summary={"findings": [f.id for f in report.findings]},
                                rules_version=rules_version
                            )
                        return report
                except Exception as e:
                    logger.warning(f"Cache error (will continue without cache): {e}")

            # 3. РџРѕР»РЅС‹Р№ Р°РЅР°Р»РёР·
            report = self._run_core(patient, raw_text)

            # 4. РЎРѕС…СЂР°РЅРµРЅРёРµ РІ РєСЌС€ (СЃ РѕР±СЂР°Р±РѕС‚РєРѕР№ РѕС€РёР±РѕРє)
            if self.cache:
                try:
                    parameters = self.parser.parse(raw_text)
                    rules_version = self._get_rules_version()
                    cache_data = {
                        "findings": [{"id": f.id, "title": f.title, "probability": f.probability,
                                      "risk": f.risk.value, "evidence": f.evidence, "description": f.description} for f in report.findings],
                        "actions": [{"doctor_specialty": a.doctor_specialty, "urgency": a.urgency.value,
                                     "additional_tests": a.additional_tests} for a in report.actions],
                        "explanation": report.explanation
                    }
                    self.cache.set(patient, parameters, rules_version, cache_data)
                except Exception as e:
                    logger.warning(f"Failed to save to cache: {e}")

            # 5. РђСѓРґРёС‚
            if self.audit_repo and user_id:
                rules_version = self._get_rules_version()
                self.audit_repo.log(
                    patient_id=patient.id,
                    user_id=user_id,
                    request_data={"raw_text": raw_text, "patient": patient},
                    result_summary={"findings": [f.id for f in report.findings]},
                    rules_version=rules_version
                )

            return report

        except MedicalAIError as e:
            logger.error(f"Domain error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            raise

    def _run_core(self, patient: PatientProfile, raw_text: str) -> AnalysisReport:
        parameters = self.parser.parse(raw_text)
        findings = self.inference_engine.infer(patient, parameters)
        actions = self.action_mapper.map_to_actions(findings)
        report = self.report_builder.build(findings, actions)
        self.history_repo.save(patient.id, report)
        return report

    def run(self, patient: PatientProfile, raw_text: str, user_id: int = None) -> str:
        report = self.run_structured(patient, raw_text, user_id)
        return self.renderer.render(report)

    def run_with_postprocessing(self, patient: PatientProfile, raw_text: str, user_id: int = None) -> Dict[str, Any]:
        report = self.run_structured(patient, raw_text, user_id)
        return self.post_processor.process(report)
