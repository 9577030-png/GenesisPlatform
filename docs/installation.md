# Installation

Consumers install only the domain package they need.

```bash
pip install genesis-medical
```

This installs `genesis-core` as a dependency.

For construction:

```bash
pip install genesis-construction
```

For the universal engine only:

```bash
pip install genesis-core
```

Applications such as `medical_app` are deployed separately from the reusable distributions.


## Domain discovery

Domain packages register a descriptor using the `genesis.domains` entry-point group. After installation, applications can call `discover_domains()` to enumerate installed domains and `load_domain(name)` to load one by registered name.

For domain developers, see [`domain-development.md`](domain-development.md).
