# Changelog

All notable changes to the Genesis Platform are documented here.

## [Unreleased]

### Platform

- Formalized independent distribution of `genesis-core`, `genesis-medical`, `genesis-construction`, and `genesis-banking`.
- Added strict Core `DomainDescriptor`, `list_domains()`, and controlled `load_domain()` errors.
- Added package compatibility matrix covering all eight Core/domain combinations.
- Added domain template generation through `scripts/create_domain.py`.
- Added CI quality gates for Ruff, strict Mypy, import-cycle analysis, tests, and dependency auditing.
- Added package-specific release workflows and SemVer checks.
- Added architecture, release, packaging, entry-point, and domain-development documentation.

### Genesis Core 0.3.0

- Stabilized the public API declaration in `src/genesis_core/api.py`.
- Added API stability tests and automated version-bump enforcement.

### Genesis Medical 0.3.0

- Completed migration of medical domain semantics and expert knowledge out of `medical_app`.
- `medical_app` now consumes `genesis-medical` as an application dependency.

### Genesis Construction 0.2.0

- Added Construction domain package and entry-point registration.

### Genesis Banking 0.1.0

- Added Banking domain proof-of-concept using the unchanged Core API.
