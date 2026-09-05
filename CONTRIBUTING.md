# Contributing to Genesis Platform

## Rules

- Keep `genesis-core` domain-neutral.
- New domain semantics belong in `genesis_<domain>`.
- Do not add dependencies between domain packages.
- Public Core API changes require a MINOR or MAJOR version bump.
- Run `pytest -q` before opening a pull request.
- Build every affected wheel when packaging metadata changes.

## New domain

Follow `docs/domain-development.md`.

## Mandatory quality gates

Pull requests must pass Ruff, strict Mypy for `src/`, import-cycle analysis, tests, and `pip-audit`.
Core API changes also require a MINOR-or-MAJOR Core version bump.
