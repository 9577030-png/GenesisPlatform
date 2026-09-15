# Genesis application

`genesis_app` is a deployable application layer, not a reusable Genesis domain distribution.

Its role is to orchestrate installed domain packages through Genesis Core contracts and application-level services.

```text
genesis_app
   |
   +-- discovers installed domains via genesis.domains
   +-- discovers installed domain resolvers via genesis.app.resolvers
   +-- executes domains through the generic DomainRuntime
   +-- retains Medical-specific application services where required
```

Domain packages are installed and deployed independently from the application.

## Dependency model

The application currently requires:

```text
genesis-app
   +-- genesis-medical>=0.3,<0.4
   +-- application infrastructure dependencies
```

`genesis-banking` and `genesis-construction` are independently installable domain plugins. When installed, their domain descriptors and application-level resolvers are discovered through entry points.

Deployment-specific dependencies such as FastAPI, Streamlit, SQLAlchemy, Redis, and authentication libraries remain application dependencies.

## Medical knowledge

Medical thresholds, reference ranges, guidelines, recommendations, and related knowledge are owned by `genesis-medical`. The application does not maintain a second YAML knowledge tree.

## Data migration status

The application database models contain `rule_versions` and `audit_logs`. Medical knowledge remains file-based and is owned by `genesis-medical`; no separate database migration is required for those knowledge assets in the current layout.
