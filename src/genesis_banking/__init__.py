from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version as _distribution_version
from importlib.resources import files
from pathlib import Path

from .domain.descriptor import BankingDomainDescriptor
from .parsers import BankingRuleParser
from .resolvers import BankingRuleResolver
from .sources import YamlBankingRuleSource

try:
    __version__ = _distribution_version("genesis-banking")
except PackageNotFoundError:
    __version__ = "0.0.0"


def get_domain_descriptor() -> BankingDomainDescriptor:
    knowledge_path = Path(str(files("genesis_banking").joinpath("knowledge")))
    return BankingDomainDescriptor(
        package="genesis_banking",
        version=__version__,
        knowledge_path=knowledge_path,
    )


__all__ = [
    "BankingDomainDescriptor",
    "BankingRuleParser",
    "BankingRuleResolver",
    "YamlBankingRuleSource",
    "get_domain_descriptor",
    "__version__",
]
