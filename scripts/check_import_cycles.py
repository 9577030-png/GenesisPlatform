from __future__ import annotations

import ast
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "src"
PACKAGES = {p.name for p in ROOT.iterdir() if p.is_dir() and (p / "__init__.py").exists()}


def imports_for(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    result: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            result.extend(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            result.append(node.module.split(".", 1)[0])
    return result


def main() -> int:
    graph: dict[str, set[str]] = defaultdict(set)
    for package in PACKAGES:
        for path in (ROOT / package).rglob("*.py"):
            for imported in imports_for(path):
                if imported in PACKAGES and imported != package:
                    graph[package].add(imported)

    visiting: set[str] = set()
    visited: set[str] = set()
    stack: list[str] = []

    def dfs(node: str) -> list[str] | None:
        if node in visiting:
            return stack[stack.index(node):] + [node]
        if node in visited:
            return None
        visiting.add(node)
        stack.append(node)
        for neighbor in graph[node]:
            cycle = dfs(neighbor)
            if cycle:
                return cycle
        stack.pop()
        visiting.remove(node)
        visited.add(node)
        return None

    for package in PACKAGES:
        cycle = dfs(package)
        if cycle:
            print("IMPORT CYCLE:", " -> ".join(cycle))
            return 1
    print("IMPORT CYCLES: NONE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
