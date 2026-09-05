# Versioning policy

Genesis distributions use Semantic Versioning and are versioned independently.

## genesis-core

Current version: `0.3.0`.

A major release is required for breaking changes to public Core contracts, including incompatible changes to exported types, constructor signatures, evaluator semantics, or extension contracts.

A minor release adds backward-compatible public functionality.

A patch release contains backward-compatible fixes and documentation changes.

## Domain packages

Domain distributions are versioned independently from Core and from one another.

Current versions:

```text
genesis-core          0.3.0
genesis-medical        0.3.0
genesis-construction   0.2.0
```

A domain package declares a compatible Core version range in its package metadata.

Changing domain expert knowledge does not require a Core release unless Core API or execution semantics also change.

## Current package versions

The reusable Genesis packages are versioned independently:

```text
genesis-core          0.3.0
genesis-medical       0.3.0
genesis-construction  0.2.0
```

## Release tags

Use package-specific Git tags because distributions are versioned independently:

```text
genesis-core-v0.3.0
genesis-medical-v0.3.0
genesis-construction-v0.2.0
```

A Core public API change must increase the Core MINOR or MAJOR version. The CI version-bump check rejects a PR that changes `src/genesis_core/api.py` without such a bump.

## Public API bump rule in CI

The CI checker compares the pull request base version with the current package manifest. If `src/genesis_core/api.py` changes, `genesis-core` must increase the MINOR or MAJOR component. A patch-only bump is rejected.

The current Core public API change therefore moves `genesis-core` from `0.2.0` to `0.3.0`. Domain package versions are independent and are bumped according to their own public API and dependency changes.

## Release source of truth

Package versions live in each package's `pyproject.toml`. Git tags identify releases independently:

- `genesis-core-vX.Y.Z`
- `genesis-medical-vX.Y.Z`
- `genesis-construction-vX.Y.Z`
- `genesis-banking-vX.Y.Z`

A separate versions file is intentionally not maintained, avoiding duplicate version sources.
