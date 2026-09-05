# Genesis Platform Architecture Specification

**Status: normative.** This document is the architectural constitution of the Genesis Platform. Changes to these rules require an explicit architectural decision and an update to this document.

## 1. Purpose

Genesis is a platform for independently distributable domain modules built on a common, domain-neutral rule engine.

The platform consists of one universal package, `genesis-core`, and independently versioned domain packages such as `genesis-medical`, `genesis-construction`, and `genesis-banking`.

## 2. Core responsibilities

`genesis-core` owns only domain-neutral mechanisms:

- `Fact`
- `Condition`
- `Rule`
- `RuleSet`
- `Evaluator`
- `RuleEngine`
- `Evidence`
- `RuleEvaluation`
- source/parser/loader/resolver/output contracts
- domain discovery through the `genesis.domains` entry-point group

Core must not contain domain terminology, expert knowledge, domain-specific data files, or imports from a domain package.

## 3. Domain responsibilities

A domain package owns its own semantics, expert knowledge, parsers, sources, resolvers, adapters, and domain-specific result interpretation.

Current domain packages:

```text
Genesis
├── genesis-core
├── genesis-medical
├── genesis-construction
└── genesis-banking
```

Dependency direction is one-way:

```text
genesis-medical      ──→ genesis-core
genesis-construction ──→ genesis-core
genesis-banking      ──→ genesis-core
```

Domain packages must not depend on one another.

Deployable applications consume domain packages; they are not part of Core.

## 4. Public Core API

The public API is declared in `src/genesis_core/api.py` and re-exported by `src/genesis_core/__init__.py`.

The API is tested for exported symbols and key signatures. Private implementation details are not part of the compatibility contract.

## 5. Domain contract and entry points

Each installable domain exposes `get_domain_descriptor()` and registers it under:

```toml
[project.entry-points."genesis.domains"]
medical = "genesis_medical:get_domain_descriptor"
```

`DomainDescriptor` requires:

- `name`
- `package`
- `version`
- `get_rule_loader()`

Core exposes:

```python
list_domains()
load_domain("medical")
```

Unknown domains must raise `LookupError` with a domain-specific message, never a leaked `KeyError` from package metadata internals.

## 6. Packaging model

The repository is a monorepo, but each reusable distribution is independent:

```text
genesis-core
genesis-medical
genesis-construction
genesis-banking
```

Production source code lives under `src/`; tests live under `tests/`; application code lives under `apps/`; package manifests live under `packages/`.

Package versions are independent and are declared in each package's own `pyproject.toml`.

Build artifacts (`build/`, `dist/`, `*.egg-info/`, caches) are generated and must not be committed.

## 7. Compatibility policy

Every supported combination of Core and installed domains must be tested from actual wheels. The compatibility matrix contains eight combinations:

1. Core
2. Core + Medical
3. Core + Construction
4. Core + Banking
5. Core + Medical + Construction
6. Core + Medical + Banking
7. Core + Construction + Banking
8. Core + Medical + Construction + Banking

A domain-only change must not require a Core change.

The successful Banking proof-of-concept is an architectural acceptance test: Banking was integrated without modifying `src/genesis_core`.

## 8. CI/CD and quality gates

Required checks are:

- Ruff
- strict Mypy for `src/`
- import-cycle analysis
- complete test suite
- dependency audit
- wheel build
- clean-wheel installation
- entry-point discovery
- compatibility matrix
- template generator test
- Core API version-bump enforcement

Core changes trigger all supported domain tests. Domain-only changes run the affected domain workflow.

## 9. Extending Core

A domain must first attempt to express new requirements with existing Core abstractions.

Only a capability that is demonstrably domain-neutral may be added to Core.

The following is forbidden:

```text
domain-specific requirement
        ↓
new domain-specific Core class
```

The intended process is:

```text
domain requirement
        ↓
identify the generic abstraction
        ↓
add generic Core capability only when necessary
```

## 10. Versioning

All distributions use Semantic Versioning independently.

For Core:

- PATCH: compatible fixes/documentation changes.
- MINOR: compatible public additions.
- MAJOR: breaking API or execution-semantics changes.

While Core is below `1.0.0`, a public API change requires at least a MINOR bump. After `1.0.0`, breaking changes require a MAJOR bump.

## 11. Release process

Releases use package-specific tags:

```text
genesis-core-vX.Y.Z
genesis-medical-vX.Y.Z
genesis-construction-vX.Y.Z
genesis-banking-vX.Y.Z
```

The release workflow builds and publishes only the package represented by the tag.

`genesis-core 1.0.0` may be released only after all quality gates and the complete compatibility matrix are green.

## 12. New-domain procedure

The supported generator is:

```powershell
python scripts/create_domain.py insurance
```

The generated package is a skeleton. A developer must implement domain-specific parsing, loading, resolution, adapters, knowledge, tests, package metadata, and entry-point registration.

See `docs/domain-development.md` for the executable template and contract.

## 13. Architectural change control

An architectural change must state:

1. why an existing rule is insufficient;
2. which package owns the new responsibility;
3. why the change does not introduce circular domain dependencies;
4. which tests and CI gates prove compatibility;
5. which versioning consequences apply.

This section is mandatory for future changes to package boundaries or Core responsibilities.
