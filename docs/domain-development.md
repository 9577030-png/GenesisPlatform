# Developing a Genesis domain package

A Genesis domain is an independently distributable Python package that depends on `genesis-core` and owns all domain-specific semantics and knowledge.

## Create a domain from the template

From the repository root:

```powershell
python scripts/create_domain.py insurance
```

This creates:

```text
src/genesis_insurance/
tests/unit/genesis_insurance/
packages/genesis-insurance/pyproject.toml
```

The generated package is intentionally a skeleton. Implement the domain-specific `RuleSource`, `RuleParser`, resolver, adapters, and knowledge files.

## Descriptor

A domain exposes a descriptor implementing the Core contract:

```python
from genesis_core.contracts import DomainDescriptor, RuleLoader


class InsuranceDomainDescriptor(DomainDescriptor):
    def __init__(self, package: str, version: str) -> None:
        super().__init__(name="insurance", package=package, version=version)

    def get_rule_loader(self) -> RuleLoader:
        return InsuranceRuleLoader(...)
```

## Entry point

```toml
[project.entry-points."genesis.domains"]
insurance = "genesis_insurance:get_domain_descriptor"
```

After installation:

```python
from genesis_core import list_domains, load_domain

print(list_domains())
insurance = load_domain("insurance")
loader = insurance.get_rule_loader()
```

Unknown domains raise `LookupError`.

## Example: Banking

`genesis_banking` is the reference proof-of-concept for a second domain. A new domain should follow the same package shape without copying banking-specific knowledge.

The architectural rule is simple: domain logic goes in the domain package; universal execution mechanisms go in `genesis-core`.

## Tests and release

Run the domain tests first, then build and install the wheel in a clean environment. CI performs the full package-isolation and entry-point checks.

## Automated template

The portable generator is `scripts/create_domain.py`:

```powershell
python scripts/create_domain.py insurance
```

The generated package is a skeleton and intentionally contains no domain knowledge. Replace its parser/source/resolver implementation, add knowledge, set the independent package version, and register the entry point.
