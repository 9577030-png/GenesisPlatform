# Core API stability

The public API of `genesis-core` is declared in `src/genesis_core/api.py` and re-exported by `src/genesis_core/__init__.py`.

The public API is covered by `tests/unit/genesis_core/test_public_api.py`, which checks both the exported symbol set and the signatures of the key public entry points.

`API_VERSION` is the API contract identifier and is independent from the package release version.

## Compatibility policy

Core uses Semantic Versioning:

- MAJOR: incompatible public API or execution-semantics changes.
- MINOR: backward-compatible public additions.
- PATCH: backward-compatible fixes and documentation changes.

A domain package must not require undocumented or private Core symbols.
