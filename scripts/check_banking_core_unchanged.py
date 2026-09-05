from __future__ import annotations

import subprocess
import sys


def main() -> int:
    command = [
        "git",
        "diff",
        "--exit-code",
        "origin/main",
        "--",
        "src/genesis_core",
    ]
    result = subprocess.run(command, check=False)
    if result.returncode == 0:
        print("BANKING CORE DIFF: NONE")
        return 0
    if result.returncode == 1:
        print("BANKING CORE DIFF: DETECTED", file=sys.stderr)
        return 1
    print("Unable to compare src/genesis_core with origin/main", file=sys.stderr)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
