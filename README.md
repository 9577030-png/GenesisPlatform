# Genesis Platform

Genesis is a modular rule-engine platform distributed as independent Python packages from one monorepository.

```text
                    Genesis Platform
                          │
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
     genesis-core   genesis-medical   genesis-construction   genesis-banking
```

## Packages

| Distribution | Purpose | Current version |
| --- | --- | --- |
| `genesis-core` | Universal rule execution and extension contracts | `0.3.0` |
| `genesis-medical` | Medical domain logic and expert knowledge | `0.3.0` |
| `genesis-construction` | Construction domain logic and knowledge | `0.2.0` |
| `genesis-banking` | Banking domain logic and knowledge | `0.1.0` |

Each reusable package has its own `pyproject.toml` under `packages/` and its own version. The deployable `medical_app` application has its own application manifest under `apps/medical_app/pyproject.toml`.

## Architecture rule

Domain packages depend on `genesis-core`. Core does not depend on domains, and domain packages do not depend on one another.

```text
genesis-medical      ──→ genesis-core

genesis-construction ──→ genesis-core
genesis-banking      ──→ genesis-core
```

Applications consume domain packages. For example:

```text
medical_app → genesis-medical → genesis-core
```

## Source layout

```text
src/      production packages
tests/    tests
apps/     deployable applications
packages/ packaging manifests
docs/     architecture and developer documentation
```

Generated build artifacts are excluded from the repository by `.gitignore`.

## Domain discovery

Installed domain packages register through the `genesis.domains` entry-point group.

```python
from genesis_core import discover_domains, load_domain

for domain in discover_domains():
    print(domain.name, domain.package, domain.version)
```

See [`docs/domain-development.md`](docs/domain-development.md) for the complete developer contract, including the required entry-point registration.

## Development

```bash
pytest -q
```

External infrastructure tests live under `tests/integration/external/` and are skipped when optional dependencies are unavailable.

## CI and release

CI installs all four distributions independently, runs the test suite, builds three wheels, and verifies package isolation.

A package-specific version tag (`genesis-core-v*`, `genesis-medical-v*`, or `genesis-construction-v*`) triggers release of that distribution only. Publishing to PyPI requires the repository secret `PYPI_API_TOKEN`. The package manifests under `packages/` are the source packaging metadata; they are not generated artifacts.

## Medical application dependency

`medical_app` is a deployable application and explicitly requires `genesis-medical>=0.3,<0.4`. It does not belong to the reusable `genesis-core`, `genesis-medical`, or `genesis-construction` distributions.
