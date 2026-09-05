# Medical domain migration

Stage 4 completes the separation of medical domain logic from `medical_app`.

## Moved to `genesis-medical`

The reusable medical package owns:

- medical domain entities and value objects;
- rule compilation and medical condition adapters;
- medical rule parsing and sources;
- conflict and rule resolvers;
- threshold resolution;
- physiological-range validation;
- clinical interpretation;
- medical post-processing, grouping, exclusions, and combinations;
- recommendation mapping and report construction;
- bundled medical knowledge.

## Remains in `medical_app`

The application owns deployment-specific concerns:

- FastAPI and Streamlit entry points;
- authentication and authorization;
- SQL/SQLite repositories;
- Redis cache;
- audit persistence;
- configuration and environment variables;
- application orchestration and HTTP/UI models.

The intended dependency direction is:

```text
medical_app
    ↓
genesis-medical
    ↓
genesis-core
```

There are no imports from `genesis_medical` back into `medical_app`.

## Knowledge loading

Medical knowledge is loaded from the installed `genesis-medical` package. The package exposes `knowledge_dir()` for application components that genuinely need a filesystem path, while its own loaders use `importlib.resources`.

There is no second `medical_app/knowledge` tree.

## Tests

Medical domain tests live outside production sources under:

```text
tests/unit/genesis_medical/
tests/integration/
```

Application-only tests live under `tests/unit/medical_app/` when present. External infrastructure tests live under `tests/integration/external/`.
