from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

from packaging.version import Version


def git_text(*args: str) -> str:
    return subprocess.check_output(["git", *args], text=True, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True)
    parser.add_argument("--current", default="HEAD")
    parser.add_argument("--api-path", default="src/genesis_core/api.py")
    parser.add_argument("--version-file", default="packages/genesis-core/pyproject.toml")
    args = parser.parse_args()

    changed = git_text("diff", "--name-only", args.base, args.current).splitlines()
    if args.api_path not in changed:
        print("CORE API: unchanged")
        return 0

    old = git_text("show", f"{args.base}:{args.version_file}")
    current = Path(args.version_file).read_text(encoding="utf-8")
    import re
    old_version = Version(re.search(r'version = "([^"]+)"', old).group(1))
    current_version = Version(re.search(r'version = "([^"]+)"', current).group(1))

    if current_version.major != old_version.major and current_version > old_version:
        return 0
    if current_version.minor > old_version.minor:
        print(f"CORE API bump: {old_version} -> {current_version}")
        return 0

    raise SystemExit(
        f"Core public API changed but version did not receive a MINOR-or-MAJOR bump: "
        f"{old_version} -> {current_version}"
    )


if __name__ == "__main__":
    raise SystemExit(main())
