# Genesis architecture

Genesis is a monorepo for a universal rule-engine platform with independently distributable domain packages.

```text
                    Genesis Platform
                          │
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
     genesis-core   genesis-medical   genesis-construction
          ▲               ▲               ▲
          └──────── domain packages ───────┘
```

The dependency direction is one-way:

```text
genesis-medical      ──→ genesis-core
genesis-construction ──→ genesis-core
genesis-banking      ──→ genesis-core
```

`genesis-core` never imports a domain package. Domain packages may contain domain-specific parsers, knowledge, resolvers, and adapters.

Applications consume installed domain packages through Core contracts and application-level orchestration:

```text
genesis_app
  -> discovers installed domains via genesis.domains
  -> discovers installed domain resolvers via genesis.app.resolvers
  -> executes them through the generic DomainRuntime
```

Domain packages remain independently distributable and may be installed or omitted according to deployment needs.

## Source layout

Production packages live under `src/`.

Tests live outside source packages under `tests/`.

Packaging manifests live under `packages/`. They are source metadata, not generated build artifacts.


## Package boundaries

`packages/` contains source packaging manifests for the reusable distributions; it is intentionally separate from generated `build/` and `dist/` output. `apps/` contains deployable applications.

The application package currently depends explicitly on genesis-medical>=0.3,<0.4 for its Medical-specific application services. Other domain packages are independently installable plugins discovered through entry points.
