# Genesis entry-point registry

Genesis domains register under the Python entry-point group `genesis.domains`.

A domain package must expose a zero-argument `get_domain_descriptor()` factory returning a `DomainDescriptor`.

The descriptor contract contains:

- `name`: stable discovery name
- `package`: import package name
- `version`: independent domain version
- `get_rule_loader()`: returns that domain's `RuleLoader`

Core APIs:

```python
from genesis_core import list_domains, discover_domains, load_domain
```

`list_domains()` is intended for diagnostics and CLI commands. `load_domain(name)` raises `LookupError` for an unknown domain and validates the descriptor type.

Core never imports a named domain directly; discovery works from installed package metadata.
