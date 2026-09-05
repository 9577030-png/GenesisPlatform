# Repository layout

```text
GenesisPlatform/
├── src/                  # reusable Python packages
├── apps/                 # deployable applications
├── tests/                # repository test suite
├── packages/             # packaging manifests only
├── docs/
└── .github/workflows/
```

`packages/` intentionally stores package-level `pyproject.toml` files. Generated `build/`, `dist/`, `*.egg-info/`, caches, and virtual environments are excluded by `.gitignore`.
