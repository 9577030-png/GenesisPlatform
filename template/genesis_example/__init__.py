from __future__ import annotations

from genesis_core import DomainDescriptor, RuleLoader

from .domain.descriptor import ExampleDomainDescriptor

__version__ = "0.1.0"


def get_domain_descriptor() -> DomainDescriptor:
    return ExampleDomainDescriptor(
        package="genesis_example",
        version=__version__,
    )


__all__ = ["ExampleDomainDescriptor", "get_domain_descriptor", "__version__"]
