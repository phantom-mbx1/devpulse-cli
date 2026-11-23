from __future__ import annotations

import argparse
import os
import platform
import shutil
import sys

DESCRIPTION = "Display local system runtime, CPU cores, and disk capacity telemetry"


def register(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--path", default=".", help="Filesystem path to check disk space (default: current dir)")


def run(args: argparse.Namespace) -> int:
    total, used, free = shutil.disk_usage(args.path)
    gb = 1024 ** 3
    used_pct = (used / total) * 100 if total else 0.0

    print("\nSystem & Runtime Telemetry")
    print("-" * 48)
    print(f"OS / Platform   : {platform.system()} {platform.release()} ({platform.machine()})")
    print(f"Python Runtime  : {platform.python_version()} ({sys.executable})")
    print(f"Logical CPUs    : {os.cpu_count() or 'Unknown'}")
    print(f"Disk Total      : {total / gb:.2f} GB")
    print(f"Disk Free       : {free / gb:.2f} GB ({100 - used_pct:.1f}% free)")
    print()
    return 0