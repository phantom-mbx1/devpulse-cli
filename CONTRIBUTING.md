# Contributing to DevPulse CLI

Thank you for helping grow **DevPulse CLI**! Every module you contribute helps developers audit their environments faster and safer.

## Security & Architecture Rules (Mandatory)
All plugins pass through an automated AST (Abstract Syntax Tree) security gatekeeper before execution and during CI checks:
1. **Zero Third-Party Dependencies:** Use only the Python 3.10+ standard library.
2. **No Unsafe Execution:** `eval`, `exec`, `compile`, `__import__`, `os.system`, `os.popen`, `pickle`, and `subprocess(..., shell=True)` are strictly blocked.
3. **Safe Network & File Defaults:** Never scan non-loopback IP addresses without an explicit opt-in flag (`--allow-remote`), and never follow symlinks blindly during directory walks.
4. **Standard Exit Codes:** Return `0` on clean checks, `1` on runtime/input errors, and `2` when security warnings/leaks are detected.

## How to Add a Plugin in 3 Minutes

1. **Fork & Branch**
   ```bash
   git checkout -b feat/my-plugin