# Genesis Medical

`genesis-medical` is an independently versioned medical domain package built on `genesis-core`.

It owns medical semantics and medical expert knowledge, including:

- medical domain entities and value objects;
- laboratory parameter normalization and parsing;
- medical rule compilation and adapters;
- clinical thresholds, guidelines, recommendations, and reference intervals;
- medical conflict resolution.

The package does not depend on `medical_app` and does not contain web, database, Redis, or authentication infrastructure.

## Install

```bash
pip install genesis-medical
```

`genesis-core` is installed automatically as a compatible dependency.

## Core usage

```python
from genesis_core import Fact, RuleEngine
from genesis_medical import RegexParser, YamlThresholdLoader
```

## Domain discovery

The package registers itself as `medical` in the `genesis.domains` entry-point group. Applications can discover installed domains through `genesis_core.discover_domains()`.
