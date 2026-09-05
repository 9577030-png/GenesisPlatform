from __future__ import annotations

import argparse
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]


def validate_name(name: str) -> str:
    normalized = name.strip().lower().replace("-", "_")
    if not normalized.isidentifier():
        raise ValueError("Domain name must be a valid Python identifier")
    if normalized in {"core", "example"}:
        raise ValueError("Reserved domain name")
    return normalized


def replace_tree(path: Path, old: str, new: str) -> None:
    for item in sorted(path.rglob("*"), reverse=True):
        if item.is_file():
            text = item.read_text(encoding="utf-8")
            text = text.replace(old, new)
            item.write_text(text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a Genesis domain from the template")
    parser.add_argument("domain", help="domain name, e.g. insurance")
    args = parser.parse_args()

    domain = validate_name(args.domain)
    package = f"genesis_{domain}"
    source = ROOT / "template" / "genesis_example"
    tests_source = ROOT / "template" / "tests" / "unit" / "genesis_example"
    target = ROOT / "src" / package
    tests_target = ROOT / "tests" / "unit" / package
    package_dir = ROOT / "packages" / f"genesis-{domain}"

    for destination in (target, tests_target, package_dir):
        if destination.exists():
            raise SystemExit(f"Refusing to overwrite existing path: {destination}")

    shutil.copytree(source, target)
    shutil.copytree(tests_source, tests_target)
    package_dir.mkdir(parents=True)
    shutil.copy(ROOT / "template" / "genesis-example-pyproject.toml", package_dir / "pyproject.toml")
    shutil.copy(ROOT / "template" / "genesis_example" / "README.md", package_dir / "README.md")

    replace_tree(target, "genesis_example", package)
    replace_tree(tests_target, "genesis_example", package)
    replace_tree(package_dir, "genesis_example", package)
    replace_tree(target, "ExampleDomainDescriptor", f"{domain.title().replace('_', '')}DomainDescriptor")
    replace_tree(target, 'name="example"', f'name="{domain}"')
    replace_tree(package_dir, "genesis-example", f"genesis-{domain}")
    replace_tree(package_dir, "example", domain)

    print(f"Created domain package: {package}")
    print(f"Source: {target}")
    print(f"Tests:  {tests_target}")
    print(f"Manifest: {package_dir / 'pyproject.toml'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
