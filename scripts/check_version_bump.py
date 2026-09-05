from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path


def run_git(*args: str) -> str:
    return subprocess.check_output(["git", *args], text=True).strip()


def read_version(text: str) -> tuple[int, int, int]:
    match = re.search(r'^version\s*=\s*["\'](\d+)\.(\d+)\.(\d+)["\']', text, re.MULTILINE)
    if not match:
        raise SystemExit("Could not find static project version")
    return tuple(int(part) for part in match.groups())


def changed(base: str, path: str) -> bool:
    output = run_git("diff", "--name-only", base, "HEAD", "--", path)
    return bool(output)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True)
    parser.add_argument("--package", required=True)
    parser.add_argument("--api-path", required=True)
    args = parser.parse_args()

    manifest = Path("packages") / args.package / "pyproject.toml"
    if not changed(args.base, args.api_path):
        print("Public API file unchanged; no version bump required.")
        return

    current_version = read_version(manifest.read_text(encoding="utf-8"))
    base_text = run_git("show", f"{args.base}:packages/{args.package}/pyproject.toml")
    base_version = read_version(base_text)

    if current_version[0] > base_version[0] or current_version[1] > base_version[1]:
        print(f"API change detected: {base_version} -> {current_version} (MINOR/MAJOR bump OK)")
        return

    raise SystemExit(
        f"API change detected in {args.api_path}, but {args.package} version "
        f"did not receive a MINOR or MAJOR bump: {base_version} -> {current_version}"
    )


if __name__ == "__main__":
    main()
