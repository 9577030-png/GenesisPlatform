import logging
from typing import List

from genesis_medical.adapters.condition_finding_mapper import (
    ConditionFindingMapper,
)
from genesis_medical.adapters.rule_compiler import RuleCompiler
from genesis_core import Fact, RuleEngine
from genesis_medical.domain.entities.finding import ClinicalFinding
from genesis_medical.domain.entities.parameter import Parameter
from genesis_medical.domain.entities.patient import PatientProfile
from medical_app.application.ports.rule_repository import RuleRepository
from genesis_medical.application.conflict_resolver import ConflictResolver

logger = logging.getLogger(__name__)


class InferenceEngine:
    def __init__(
        self,
        rule_repo: RuleRepository,
        threshold_provider,
        guideline_provider,
    ):
        self.rule_repo = rule_repo
        self.threshold_provider = threshold_provider
        self.guideline_provider = guideline_provider
        self.rule_engine = RuleEngine()
        self.conflict_resolver = ConflictResolver()

    def infer(
        self,
        patient: PatientProfile,
        parameters: List[Parameter],
    ) -> List[ClinicalFinding]:
        logger.info(
            "Inference for patient %s (gender=%s)",
            patient.id,
            patient.gender.value,
        )

        facts = self._build_facts(parameters)

        active_rules = self.rule_repo.get_active_versions()

        rules_dict = {
            rule.rule_id: rule
            for rule in active_rules
        }

        compiled_rules = []

        for rule_version in active_rules:
            compiled_rules.extend(
                RuleCompiler.compile(
                    rule_version,
                    patient_gender=patient.gender,
                )
            )

        evaluations = self.rule_engine.evaluate(
            [item.rule for item in compiled_rules],
            facts,
        )

        findings: List[ClinicalFinding] = []
        finding_rule_ids: dict[str, str] = {}

        for compiled_rule, evaluation in zip(
            compiled_rules,
            evaluations,
        ):
            if not evaluation.matched:
                continue

            finding = ConditionFindingMapper.to_finding(
                compiled_rule.condition,
                compiled_rule.rule_version,
            )

            findings.append(finding)

            finding_rule_ids[finding.id] = (
                compiled_rule.rule_version.rule_id
            )

            logger.debug(
                "Rule %s / condition %s matched",
                compiled_rule.rule_version.rule_id,
                compiled_rule.condition.get(
                    "id",
                    compiled_rule.rule_version.rule_id,
                ),
            )

        findings = self.conflict_resolver.resolve(
            findings,
            rules_dict,
            finding_rule_ids,
        )

        logger.info(
            "Inference complete: %s findings after "
            "conflict resolution",
            len(findings),
        )

        return findings

    @staticmethod
    def _build_facts(
        parameters: List[Parameter],
    ) -> list[Fact]:
        return [
            Fact(
                name=parameter.name.lower(),
                value=parameter.value,
                unit=str(parameter.unit),
            )
            for parameter in parameters
        ]
