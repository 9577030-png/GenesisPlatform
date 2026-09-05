from unittest.mock import Mock

from genesis_medical.services import PostProcessor
from genesis_medical.domain.entities.finding import ClinicalFinding
from genesis_medical.domain.entities.report import AnalysisReport
from genesis_medical.domain.value_objects.risk_level import RiskLevel


def make_processor(
    *,
    threshold: float = 0.3,
    exclusions=None,
    combinations=None,
    system_groups=None,
):
    loader = Mock()

    loader.get_config.return_value = {
        "probability_threshold": {
            "default": threshold,
        },
        "exclusions": exclusions or [],
        "combinations": combinations or [],
        "system_groups": system_groups or {},
    }

    loader.get_diagnosis_labels.return_value = {}
    loader.get_system_groups.return_value = system_groups or {}
    loader.get_allowed_primary.return_value = []

    return PostProcessor(
        logic_loader=loader,
        probability_threshold=threshold,
    )


def make_finding(
    finding_id: str,
    probability: float = 0.5,
    risk: RiskLevel = RiskLevel.HIGH,
):
    return ClinicalFinding(
        id=finding_id,
        title=finding_id,
        probability=probability,
        risk=risk,
    )


def make_report(*findings):
    return AnalysisReport(
        findings=list(findings),
        actions=[],
        explanation="",
    )


def test_probability_threshold_filters_findings():
    processor = make_processor(threshold=0.3)

    report = make_report(
        make_finding("low", 0.2),
        make_finding("high", 0.4),
    )

    result = processor.process(report)

    ids = {d["id"] for d in result["diagnoses"]}

    assert "low" not in ids
    assert "high" in ids


def test_exclusion_removes_base_finding():
    processor = make_processor(
        exclusions=[
            {
                "if": "sepsis",
                "then": ["systemic_inflammation"],
            }
        ]
    )

    report = make_report(
        make_finding("sepsis", 0.9),
        make_finding("systemic_inflammation", 0.7),
    )

    result = processor.process(report)

    ids = {d["id"] for d in result["diagnoses"]}

    assert "sepsis" in ids
    assert "systemic_inflammation" not in ids


def test_exclusion_matches_parameterized_finding_id():
    processor = make_processor(
        exclusions=[
            {
                "if": "creatinine_high",
                "then": ["creatinine_high_female"],
            }
        ]
    )

    report = make_report(
        make_finding("creatinine_high_female", 0.8),
    )

    result = processor._apply_exclusions(
        report.findings
    )

    assert result == []


def test_system_group_contains_matching_findings():
    processor = make_processor(
        system_groups={
            "kidney": [
                "chronic_kidney_disease",
                "acute_kidney_injury",
            ]
        }
    )

    findings = [
        make_finding("chronic_kidney_disease"),
        make_finding("unrelated"),
    ]

    grouped = processor._build_grouped(findings)

    assert "kidney" in grouped
    assert len(grouped["kidney"]) == 1
    assert (
        grouped["kidney"][0]["id"]
        == "chronic_kidney_disease"
    )


def test_combination_requires_all_conditions():
    processor = make_processor(
        combinations=[
            {
                "id": "combined",
                "label": "Combined",
                "conditions": [
                    "a",
                    "b",
                ],
            }
        ]
    )

    findings = [
        make_finding("a", 0.8),
    ]

    diagnoses, recommendations = (
        processor._apply_combinations(findings)
    )

    assert diagnoses == []
    assert recommendations == []


def test_combination_calculates_probability():
    processor = make_processor(
        combinations=[
            {
                "id": "combined",
                "label": "Combined",
                "conditions": [
                    "a",
                    "b",
                ],
                "probability_factor": 0.8,
            }
        ]
    )

    findings = [
        make_finding("a", 0.8),
        make_finding("b", 0.6),
    ]

    diagnoses, _ = processor._apply_combinations(
        findings
    )

    assert len(diagnoses) == 1
    assert diagnoses[0]["id"] == "combined"


def test_combination_below_threshold_is_ignored():
    processor = make_processor(
        threshold=0.3,
        combinations=[
            {
                "id": "combined",
                "label": "Combined",
                "conditions": [
                    "a",
                    "b",
                ],
                "probability_factor": 0.2,
            }
        ]
    )

    findings = [
        make_finding("a", 0.4),
        make_finding("b", 0.4),
    ]

    diagnoses, _ = processor._apply_combinations(
        findings
    )

    assert diagnoses == []


def test_grouped_findings_preserve_probability_and_risk():
    processor = make_processor(
        system_groups={
            "hematology": ["anemia"],
        }
    )

    findings = [
        make_finding(
            "anemia",
            probability=0.7,
            risk=RiskLevel.HIGH,
        )
    ]

    grouped = processor._build_grouped(findings)

    item = grouped["hematology"][0]

    assert item["id"] == "anemia"
    assert item["probability"] == 0.7
    assert item["risk"] == RiskLevel.HIGH.label


def test_empty_report_produces_no_diagnoses():
    processor = make_processor()

    result = processor.process(
        make_report()
    )

    assert result["diagnoses"] == []
    assert result["grouped_findings"] == {}
        
