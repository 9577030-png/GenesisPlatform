# Genesis Core public API

`genesis-core` exposes a deliberately small public API. Domain packages must depend only on these exported types and extension contracts.

## Public API

The public API is declared in `genesis_core.api` and re-exported from `genesis_core`:

```python
from genesis_core import (
    Condition,
    DefaultRuleLoader,
    DomainDescriptor,
    Evidence,
    Evaluator,
    Fact,
    OutputAdapter,
    Rule,
    RuleEngine,
    RuleEvaluation,
    RuleLoader,
    RuleParser,
    RuleResolver,
    RuleSet,
    RuleSource,
    discover_domains,
    load_domain,
)
```

`API_VERSION` identifies the public API contract. It is not the package release version.

## SemVer policy

Core follows Semantic Versioning:

- **MAJOR**: incompatible changes to exported types, constructor/method signatures, evaluator semantics, or extension contracts.
- **MINOR**: backward-compatible additions to the public API.
- **PATCH**: backward-compatible bug fixes and documentation-only changes.

Changing domain packages does not require a Core release unless the Core API or execution semantics change.

## Domain extension contracts

Domain authors implement these Core contracts:

- `RuleSource`
- `RuleParser`
- `RuleLoader`
- `RuleResolver`
- `OutputAdapter`
- `DomainDescriptor`

Core must not import a domain package. A domain package may import Core.
