# genesis-medical

`genesis-medical` is the medical domain package for the Genesis platform. It depends on `genesis-core` and owns medical-specific models, parsers, rule compilation, resolvers, services, and expert knowledge.

## Install

```bash
pip install genesis-medical
```

`genesis-core>=0.3,<0.4`, `PyYAML>=6.0`, and `pydantic>=2,<3` are declared dependencies.

## Knowledge ownership

The package ships its medical knowledge under `genesis_medical/knowledge/`, including thresholds, reference ranges, guidelines, recommendations, aliases, units, and clinical logic. Applications must consume this package API instead of keeping a second copy of the medical knowledge tree.

## Public domain API

Key exports include:

```python
from genesis_medical import (
    ClinicalInterpreter,
    MedicalReferenceLoader,
    ParameterNormalizer,
    PhysiologicalValidator,
    PostProcessor,
)
```

Bundled knowledge is available through:

```python
from genesis_medical import knowledge_dir
```

## Domain registration

The package registers itself through the `genesis.domains` entry-point group:

```toml
[project.entry-points."genesis.domains"]
medical = "genesis_medical:get_domain_descriptor"
```

This allows `genesis-core` to discover the installed domain without importing it directly.

## Application boundary

A deployable application consumes the package:

```text
medical_app → genesis-medical → genesis-core
```

`medical_app` owns HTTP, UI, authentication, persistence, caching, logging, and deployment configuration. Medical rules and medical knowledge stay in `genesis-medical`.
