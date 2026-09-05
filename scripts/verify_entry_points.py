from __future__ import annotations

from genesis_core import list_domains, load_domain


REQUIRED = {"medical", "construction"}


def main() -> None:
    discovered = set(list_domains())
    missing = REQUIRED - discovered
    if missing:
        raise SystemExit(f"Missing Genesis domains: {sorted(missing)}")

    for name in sorted(REQUIRED):
        descriptor = load_domain(name)
        if descriptor.name != name:
            raise SystemExit(
                f"Descriptor name mismatch: {descriptor.name!r} != {name!r}"
            )
        descriptor.get_rule_loader()

    print("ENTRY POINTS: OK")


if __name__ == "__main__":
    main()
