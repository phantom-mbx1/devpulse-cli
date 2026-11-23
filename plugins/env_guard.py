from __future__ import annotations

import argparse
from pathlib import Path

DESCRIPTION = "Verify .env is ignored by Git and compare keys against .env.example safely"


def _parse_env_keys(path: Path) -> set[str]:
    keys: set[str] = set()
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key = stripped.split("=", 1)[0].strip()
        if key:
            keys.add(key)
    return keys


def register(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--env-file", default=".env", help="Path to local env file (default: .env)")
    parser.add_argument("--example-file", default=".env.example", help="Path to template env file")


def run(args: argparse.Namespace) -> int:
    env_path = Path(args.env_file)
    example_path = Path(args.example_file)
    gitignore_path = Path(".gitignore")

    print("\nEnvironment Configuration & Exposure Guard")
    print("-" * 52)

    if gitignore_path.is_file():
        gi_lines = [line.strip() for line in gitignore_path.read_text(encoding="utf-8", errors="ignore").splitlines()]
        is_ignored = any(rule in {".env", "*.env", ".env*"} for rule in gi_lines)
        print(f".gitignore covers .env : {'YES' if is_ignored else 'NO [RISK]'}")
    else:
        print(".gitignore covers .env : NO .gitignore FOUND [RISK]")

    if not env_path.is_file() or not example_path.is_file():
        print(f"File status            : Missing {env_path} or {example_path}\n")
        return 0

    env_keys = _parse_env_keys(env_path)
    example_keys = _parse_env_keys(example_path)

    missing_in_env = sorted(example_keys - env_keys)
    undocumented_in_example = sorted(env_keys - example_keys)

    print(f"Keys in .env           : {len(env_keys)}")
    print(f"Keys in .env.example   : {len(example_keys)}")

    if missing_in_env:
        print(f"[WARN] Missing keys in {env_path}: {', '.join(missing_in_env)}")
    if undocumented_in_example:
        print(f"[INFO] Undocumented keys in {example_path}: {', '.join(undocumented_in_example)}")
    if not missing_in_env and not undocumented_in_example:
        print("Schema parity          : 100% synchronized")
    print()
    return 0