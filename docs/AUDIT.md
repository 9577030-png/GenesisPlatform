# Architecture audit

Current package model:

- `genesis-core` — universal engine
- `genesis-medical` — independent medical domain distribution
- `genesis-construction` — independent construction domain distribution
- `apps/medical_app` — application consuming `genesis-medical`

Build artifacts (`build/`, `dist/`, `*.egg-info/`) are generated locally and are excluded from source control and release archives.

External tests that require optional infrastructure dependencies live under `tests/integration/external/`.
