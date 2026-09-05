from genesis_core.contracts import DomainDescriptor

from .domain.descriptor import MedicalDomainDescriptor

from .domain.entities import (
    AnalysisReport,
    ClinicalFinding,
    Parameter,
    PatientProfile,
    Recommendation,
    SpecialtyGuideline,
    Threshold,
)
from .domain.rule_version import RulePriority, RuleTier, RuleVersion
from .domain.value_objects import Gender, RiskLevel, Severity, Unit
from .parsers import ParameterNormalizer, RegexParser

from .models import (
    ClinicalInsights,
    CriterionEvaluation,
    DifferentialSuggestion,
    RedFlag,
    TreatmentHint,
)
from .services import (
    ActionMapper,
    ClinicalInterpreter,
    PhysiologicalValidator,
    PostProcessor,
    ReportBuilder,
    build_explanation,
)

from .sources import (
    ClinicalLogicLoader,
    MedicalReferenceLoader,
    MergedGuidelineProvider,
    YamlGuidelineProvider,
    YamlRecommendationLoader,
    YamlThresholdLoader,
)

try:
    from importlib.metadata import version as _distribution_version
    __version__ = _distribution_version("genesis-medical")
except Exception:
    __version__ = "0.0.0"


def get_domain_descriptor() -> DomainDescriptor:
    return MedicalDomainDescriptor(
        package="genesis_medical",
        version=__version__,
        knowledge_path=knowledge_dir(),
    )


__all__ = [
    "ActionMapper",
    "AnalysisReport",
    "ClinicalFinding",
    "ClinicalInsights",
    "ClinicalInterpreter",
    "ClinicalLogicLoader",
    "CriterionEvaluation",
    "DifferentialSuggestion",
    "Gender",
    "MedicalDomainDescriptor",
    "MedicalReferenceLoader",
    "MergedGuidelineProvider",
    "Parameter",
    "ParameterNormalizer",
    "PatientProfile",
    "PhysiologicalValidator",
    "PostProcessor",
    "Recommendation",
    "RedFlag",
    "RegexParser",
    "ReportBuilder",
    "RiskLevel",
    "RulePriority",
    "RuleTier",
    "RuleVersion",
    "Severity",
    "SpecialtyGuideline",
    "Threshold",
    "TreatmentHint",
    "Unit",
    "YamlGuidelineProvider",
    "YamlMedicalRuleSource",
    "YamlRecommendationLoader",
    "YamlThresholdLoader",
    "build_explanation",
    "get_domain_descriptor",
    "knowledge_dir",
]


def knowledge_dir():
    """Return the bundled Genesis Medical knowledge directory."""
    from pathlib import Path
    from importlib.resources import files

    return Path(str(files("genesis_medical").joinpath("knowledge")))
