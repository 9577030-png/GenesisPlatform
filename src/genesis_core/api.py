from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version as _distribution_version

from .condition import Condition
from .default_rule_loader import DefaultRuleLoader
from .evaluation import Evidence, RuleEvaluation
from .evaluator import Evaluator
from .fact import Fact
from .plugin_registry import discover_domains, list_domains, load_domain
from .rule import Rule
from .rule_engine import RuleEngine
from .rule_set import RuleSet
from .contracts import (
    DomainDescriptor,
    OutputAdapter,
    RuleLoader,
    RuleParser,
    RuleResolver,
    RuleSource,
)

API_VERSION = "1"

try:
    __version__ = _distribution_version("genesis-core")
except PackageNotFoundError:
    __version__ = "0.0.0"

__all__ = [
    "API_VERSION",
    "__version__",
    "Condition",
    "DefaultRuleLoader",
    "DomainDescriptor",
    "Evidence",
    "Evaluator",
    "Fact",
    "OutputAdapter",
    "Rule",
    "RuleEngine",
    "RuleEvaluation",
    "RuleLoader",
    "RuleParser",
    "RuleResolver",
    "RuleSet",
    "RuleSource",
    "discover_domains",
    "list_domains",
    "load_domain",
]
