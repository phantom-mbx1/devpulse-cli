from __future__ import annotations

import argparse
import os
from pathlib import Path
import re
import subprocess

DESCRIPTION = "Audit Git repository status, oversized files, and accidental secret leaks"

SECRET_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("Private Key Header", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
    ("AWS Access Key ID", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("GitHub Token", re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{36,}\b")),
    ("Generic High-Risk Assignment", re.compile(r"(?i)(?:api_key|secret_key|password|passwd|token)\s*[:=]\s*['\"][A-Za-z0-9_\-]{16,}['\"]")),
]

MAX_SCAN_FILE_BYTES = 1024 * 1024  # Skip binary/huge files over 1 MB for regex scan
MAX_FILES_SCANNED = 2000


def register(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--max-mb", type=float, default=10.0, help="Flag files larger than N MB (default: 10)")
    parser.add_argument("--skip-secrets", action="store_true", help="Skip secret pattern scanning")


def _run_git(args: list[str]) -> tuple[int, str]:
    res = subprocess.run(
        ["git", *args],
        capture_output=True,
        text=True,
        timeout=10,
        shell=False,
    )
    return res.returncode, res.stdout.strip()


def run(args: argparse.Namespace) -> int:
    code, branch = _run_git(["rev-parse", "--abbrev-ref", "HEAD"])
    if code != 0:
        print("[!] Current directory is not inside a Git repository.")
        return 1

    _, status = _run_git(["status", "--short"])
    _, unpushed = _run_git(["log", "@{u}..", "--oneline"])

    print(f"\nGit Security & Hygiene Audit (Branch: {branch})")
    print("-" * 54)
    print(f"Uncommitted changes : {len(status.splitlines()) if status else 0}")
    print(f"Unpushed commits    : {len(unpushed.splitlines()) if unpushed else 0}")

    threshold_bytes = args.max_mb * 1024 * 1024
    large_files: list[tuple[str, float]] = []
    secret_hits: list[tuple[str, int, str]] = []
    scanned_count = 0

    for root, dirs, files in os.walk(".", followlinks=False):
        dirs[:] = [d for d in dirs if d not in {".git", "node_modules", "__pycache__", ".venv", "venv"}]
        for fname in files:
            if scanned_count >= MAX_FILES_SCANNED:
                break
            fpath = Path(root) / fname
            if fpath.is_symlink():
                continue

            try:
                size = fpath.stat().st_size
            except OSError:
                continue

            if size > threshold_bytes:
                large_files.append((str(fpath), size / (1024 * 1024)))

            if not args.skip_secrets and size <= MAX_SCAN_FILE_BYTES:
                scanned_count += 1
                try:
                    content = fpath.read_text(encoding="utf-8", errors="strict")
                    for line_no, line in enumerate(content.splitlines(), start=1):
                        for label, pattern in SECRET_PATTERNS:
                            if pattern.search(line):
                                secret_hits.append((str(fpath), line_no, label))
                except (UnicodeDecodeError, OSError):
                    pass

    if large_files:
        print(f"\n[WARN] Files exceeding {args.max_mb} MB:")
        for path, mb in large_files:
            print(f"  - {path} ({mb:.2f} MB)")
    else:
        print(f"Oversized files     : None over {args.max_mb} MB")

    if not args.skip_secrets:
        if secret_hits:
            print(f"\n[CRITICAL] Potential secrets detected ({len(secret_hits)}):")
            for path, line_no, label in secret_hits[:20]:
                print(f"  - {path}:{line_no} -> {label}")
            print()
            return 2
        else:
            print(f"Secret scan         : Clean ({scanned_count} text files checked)")

    print()
    return 0