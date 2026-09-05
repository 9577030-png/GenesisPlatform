# Genesis Release Process

This document defines the release process for the Genesis monorepository.

## Distribution model

Each reusable package is released independently:

- `genesis-core`
- `genesis-medical`
- `genesis-construction`
- `genesis-banking`

`medical_app` is an application and is not part of the reusable Genesis domain distributions.

Package versions are defined in their own `pyproject.toml` files. There is no second version source.

## Required checks before a release

The following checks must be green before publishing a package:

1. Ruff linting.
2. Strict Mypy for `src/`.
3. Import-cycle check.
4. Test suite.
5. Dependency audit.
6. Package build.
7. Clean-wheel installation.
8. Entry-point discovery for installed domains.
9. Compatibility matrix when `genesis-core` changes.
10. API version-bump check when `src/genesis_core/api.py` changes.

A domain-only change must not require changes to `genesis-core`.

## Semantic Versioning

Genesis uses Semantic Versioning per distribution:

- PATCH: backward-compatible bug fixes and documentation changes.
- MINOR: backward-compatible public API additions.
- MAJOR: breaking public API or execution-semantics changes.

For `genesis-core`, changing the declared public API in `src/genesis_core/api.py` requires at least a MINOR release while Core remains below 1.0.0.

When Core reaches `1.0.0`, the public API becomes stable under SemVer: breaking changes require `2.0.0` or later; compatible additions use `1.x`; fixes use `1.x.y`.

## Release tags

Use package-specific tags:

```text
genesis-core-vX.Y.Z
genesis-medical-vX.Y.Z
genesis-construction-vX.Y.Z
genesis-banking-vX.Y.Z
```

The release workflow builds and publishes only the package named by the tag.

## Release procedure

### Core

1. Ensure all CI checks are green.
2. Update `packages/genesis-core/pyproject.toml`.
3. Update `CHANGELOG.md`.
4. Verify the package wheel in a clean environment.
5. Create `genesis-core-vX.Y.Z`.
6. Push the tag.
7. GitHub Actions builds and publishes the Core wheel when `PYPI_API_TOKEN` is configured.

### Domain package

The same process applies independently to Medical, Construction, and Banking.

A domain package release may be made without releasing Core unless its declared Core compatibility range changes or Core itself changes.

## Core 1.0.0 gate

`genesis-core` must not be promoted to `1.0.0` until:

- the API stability tests are green;
- all quality gates are green in CI;
- the eight-way package compatibility matrix is green;
- all currently supported domains run against the release candidate;
- release artifacts install successfully in clean environments;
- `docs/architecture-specification.md` and `docs/api-stability.md` are current.

The 1.0.0 release is an explicit stability commitment, not merely a version-number change.
