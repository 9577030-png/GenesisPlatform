from .domain.descriptor import ConstructionDomainDescriptor
from .parsers import ConstructionRuleParser
from .resolvers import ConstructionRuleResolver
from .sources import YamlConstructionRuleSource

try:
    from importlib.metadata import version as _distribution_version
    __version__ = _distribution_version("genesis-construction")
except Exception:
    __version__ = "0.1.0"

__all__ = [
    "ConstructionDomainDescriptor",
    "ConstructionRuleParser",
    "ConstructionRuleResolver",
    "YamlConstructionRuleSource",
    "__version__",
    "get_domain_descriptor",
]


def get_domain_descriptor():
    from pathlib import Path
    from importlib.resources import files

    return ConstructionDomainDescriptor(
        package="genesis_construction",
        version=__version__,
        knowledge_path=Path(str(files("genesis_construction").joinpath("knowledge"))),
    )
