# Packaging manifests

This directory contains the packaging metadata for the independently distributable Genesis packages.

```text
packages/
├── genesis-core/pyproject.toml
├── genesis-medical/pyproject.toml
├── genesis-construction/pyproject.toml
└── genesis-banking/pyproject.toml
```

Production source code lives under `src/`. Tests live under `tests/`. Build outputs such as `dist/`, `build/`, and `*.egg-info/` are generated and must not be committed.
