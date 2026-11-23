#!/usr/bin/env python3
"""
DevPulse CLI (Hardened Edition)
Zero-dependency, AST-verified modular developer diagnostics & security audit toolkit.
"""

from __future__ import annotations

import argparse
import ast
import importlib.util
import re
import sys
from pathlib import Path
from types import ModuleType

VERSION = "2.0.0"
PLUGIN_DIR = (Path(__file__).parent / "plugins").resolve()
VALID_PLUGIN_NAME = re.compile(r"^[a-z][a-z0-9_]{1,30}$")

# Dangerous builtins/functions disallowed in community plugins
FORBIDDEN_CALLS = {
    "eval",
    "exec",
    "compile",
    "__import__",
    "os.system",
    "os.popen",
    "pickle.loads",
    "pickle.load",
    "marshal.loads",
}


class PluginSecurityError(Exception):
    """Raised when a plugin violates static security rules."""


def audit_plugin_ast(file_path: Path) -> None:
    """
    Performs static AST security inspection on a plugin before importing it.
    Blocks dangerous dynamic execution and unsafe subprocess shell usage.
    """
    source = file_path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(file_path))

    for node in ast.walk(tree):
        # Block dangerous direct or attribute calls
        if isinstance(node, ast.Call):
            func_name = _resolve_call_name(node.func)
            if func_name in FORBIDDEN_CALLS:
                raise PluginSecurityError(f"Forbidden call '{func_name}' detected in {file_path.name}")

            # Block subprocess calls with shell=True
            if func_name.startswith("subprocess."):
                for kw in node.keywords:
                    if kw.arg == "shell" and isinstance(kw.value, ast.Constant) and kw.value.value is True:
                        raise PluginSecurityError(
                            f"Unsafe 'shell=True' in {file_path.name}; use argument lists instead."
                        )


def _resolve_call_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = _resolve_call_name(node.value)
        return f"{base}.{node.attr}" if base else node.attr
    return ""


def is_safe_plugin_path(file_path: Path) -> bool:
    """Ensures plugin is a regular file strictly inside PLUGIN_DIR (no symlinks/traversal)."""
    try:
        if file_path.is_symlink() or not file_path.is_file():
            return False
        resolved = file_path.resolve()
        return resolved.parent == PLUGIN_DIR and VALID_PLUGIN_NAME.match(resolved.stem) is not None
    except OSError:
        return False


def load_plugins(strict_security: bool = True) -> dict[str, ModuleType]:
    """Safely discovers, audits, and loads all valid plugin modules."""
    plugins: dict[str, ModuleType] = {}
    if not PLUGIN_DIR.is_dir():
        return plugins

    for file_path in sorted(PLUGIN_DIR.iterdir()):
        if file_path.name.startswith("_") or file_path.suffix != ".py":
            continue

        if not is_safe_plugin_path(file_path):
            print(f"[SECURITY] Skipped invalid or symlinked plugin path: {file_path.name}", file=sys.stderr)
            continue

        try:
            if strict_security:
                audit_plugin_ast(file_path)

            module_name = f"devpulse_plugins.{file_path.stem}"
            spec = importlib.util.spec_from_file_location(module_name, str(file_path))
            if spec is None or spec.loader is None:
                continue

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            if callable(getattr(module, "register", None)) and callable(getattr(module, "run", None)):
                plugins[file_path.stem] = module
            else:
                print(f"[WARN] Plugin '{file_path.stem}' missing register() or run().", file=sys.stderr)

        except PluginSecurityError as sec_err:
            print(f"[SECURITY BLOCK] {sec_err}", file=sys.stderr)
        except Exception as exc:
            print(f"[ERROR] Failed to load plugin '{file_path.stem}': {exc}", file=sys.stderr)

    return plugins


def build_parser(plugins: dict[str, ModuleType]) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="devpulse",
        description="DevPulse CLI — Hardened, zero-dependency developer & security audit toolkit.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    subparsers = parser.add_subparsers(dest="command", required=True, help="Available audit modules")

    for name, module in plugins.items():
        desc = getattr(module, "DESCRIPTION", f"Run {name} module")
        sub = subparsers.add_parser(name, help=desc, description=desc)
        module.register(sub)

    return parser


def main(argv: list[str] | None = None) -> int:
    plugins = load_plugins(strict_security=True)
    if not plugins:
        print("[!] No valid plugins loaded.", file=sys.stderr)
        return 1

    parser = build_parser(plugins)
    args = parser.parse_args(argv)
    selected = plugins.get(args.command)

    if selected is None:
        return 1

    try:
        exit_code = selected.run(args)
        return int(exit_code) if isinstance(exit_code, int) else 0
    except KeyboardInterrupt:
        print("\n[!] Interrupted by user.", file=sys.stderr)
        return 130
    except Exception as exc:
        print(f"[ERROR] Module '{args.command}' encountered an error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())