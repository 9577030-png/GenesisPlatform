from __future__ import annotations

from collections.abc import Sequence

from ..domain.entities.finding import ClinicalFinding


def build_explanation(findings: Sequence[ClinicalFinding]) -> str:
    """Build a deterministic explanation for medical findings."""
    if not findings:
        return "No significant findings."

    parts = [
        f"- {finding.title} "
        f"(probability {finding.probability:.0%}, "
        f"risk {finding.risk.label})"
        for finding in findings
    ]
    return "Findings:\n" + "\n".join(parts)
