from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_create_domain_generates_buildable_package(tmp_path: Path) -> None:
    output_root = tmp_path / "generated"
    output_root.mkdir()

    # The generator is repository-root based, so run it in an isolated copy of
    # the repository to avoid mutating the working tree.
    import shutil

    shutil.copytree(ROOT / "template", output_root / "template")
    shutil.copytree(ROOT / "scripts", output_root / "scripts")

    result = subprocess.run(
        [sys.executable, str(output_root / "scripts" / "create_domain.py"), "insurance"],
        cwd=output_root,
        check=True,
        capture_output=True,
        text=True,
    )

    assert "Created domain package" in result.stdout
    package = output_root / "src" / "genesis_insurance"
    manifest = output_root / "packages" / "genesis-insurance" / "pyproject.toml"
    tests = output_root / "tests" / "unit" / "genesis_insurance"

    assert (package / "__init__.py").is_file()
    assert (package / "domain" / "descriptor.py").is_file()
    assert manifest.is_file()
    assert (tests / "test_import.py").is_file()
