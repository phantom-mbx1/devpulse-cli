"""
DevPulse CLI Built-In & Community Plugins Package.

Every plugin module placed in this directory must implement:
    - DESCRIPTION: str
    - def register(parser: argparse.ArgumentParser) -> None
    - def run(args: argparse.Namespace) -> int
"""

from __future__ import annotations

__all__ = [
    "cache_audit",
    "env_guard",
    "git_health",
    "net_diag",
    "port_audit",
    "sys_pulse",
]