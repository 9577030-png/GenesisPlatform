# Genesis Construction

`genesis-construction` is an independently versioned construction domain package built on `genesis-core`.

It owns construction-specific parsing, rule sources, resolvers, and domain knowledge. The bundled YAML rules are illustrative examples, not normative engineering requirements.

## Install

```bash
pip install genesis-construction
```

`genesis-core` is installed automatically as a compatible dependency.

The package registers the `construction` domain through the `genesis.domains` entry-point group.
