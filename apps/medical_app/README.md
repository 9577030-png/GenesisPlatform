# Medical application

`medical_app` is an application layer, not a reusable Genesis distribution.

Its intended dependency direction is:

```text
medical_app → genesis-medical → genesis-core
```

Install and deploy the reusable packages independently from the application.


## Dependency

The application explicitly requires `genesis-medical>=0.3,<0.4`. Deployment-specific dependencies such as FastAPI, Streamlit, SQLAlchemy, Redis, and authentication libraries remain application dependencies.

Medical knowledge is supplied by the `genesis-medical` package. The application does not maintain a second YAML knowledge tree.

## Data migration status

The application database models contain `rule_versions` and `audit_logs`. Medical thresholds, reference ranges, guidelines, and recommendations are file-based knowledge owned by `genesis-medical`; no separate database migration is required for those knowledge assets in the current layout.
