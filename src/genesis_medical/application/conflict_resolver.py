from __future__ import annotations

import logging
from typing import Dict, List, Set

from genesis_medical.domain.entities.finding import ClinicalFinding
from genesis_medical.domain.rule_version import RulePriority, RuleVersion

logger = logging.getLogger(__name__)


class ConflictResolver:
    def resolve(
        self,
        findings: List[ClinicalFinding],
        rules: Dict[str, RuleVersion],
        finding_rule_ids: Dict[str, str] | None = None,
    ) -> List[ClinicalFinding]:
        if not findings:
            return []

        finding_rule_ids = finding_rule_ids or {}

        def rule_of(finding_id: str) -> str:
            return finding_rule_ids.get(finding_id, finding_id)

        conflict_graph: Dict[str, Set[str]] = {
            rule_id: set(rule.conflicts_with)
            for rule_id, rule in rules.items()
        }

        finding_priorities = {}
        for finding in findings:
            rule = rules.get(rule_of(finding.id))
            finding_priorities[finding.id] = (
                rule.priority if rule else RulePriority.MEDIUM
            )

        sorted_findings = sorted(
            findings,
            key=lambda finding: finding_priorities.get(
                finding.id, RulePriority.MEDIUM
            ),
            reverse=True,
        )

        kept_ids: set[str] = set()
        for finding in sorted_findings:
            finding_rule = rule_of(finding.id)
            if any(
                finding_rule in conflict_graph.get(kept_rule, set())
                or kept_rule in conflict_graph.get(finding_rule, set())
                for kept_rule in (rule_of(item_id) for item_id in kept_ids)
            ):
                continue
            kept_ids.add(finding.id)

        return list(
            {
                finding.id: finding
                for finding in findings
                if finding.id in kept_ids
            }.values()
        )
