# Banking proof of platform universality

`genesis-banking` is an independent distribution that depends only on `genesis-core`.

The bundled rules are illustrative software examples. They demonstrate rule parsing, loading, multiple facts, and priority/conflict resolution without representing financial advice, credit policy, or regulatory thresholds.

## Runtime pipeline

```text
Banking YAML
    ↓
BankingRuleParser
    ↓
DefaultRuleLoader
    ↓
RuleSet
    ↓
Genesis Core RuleEngine
    ↓
BankingRuleResolver
```

## Platform proof

The Banking package must operate without changes to `src/genesis_core/`. During the Banking experiment, compare the Core tree against the main branch:

```bash
git diff origin/main -- src/genesis_core
```

The expected result is an empty diff.
