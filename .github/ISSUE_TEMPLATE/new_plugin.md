---
name: New Diagnostic Plugin Proposal
about: Propose or claim a new zero-dependency diagnostic module for DevPulse CLI
title: "[PLUGIN] "
labels: enhancement, good first issue, help wanted
assignees: ''
---

## Plugin Name
`plugins/<plugin_name>.py` (lowercase letters, numbers, and underscores only)

## Problem It Solves
Describe what developer, networking, or security issue this module audits or automates.

## Proposed CLI Flags
- `--example-flag`: Explain what this flag configures

## Security & Dependency Checklist
- [ ] Uses **only** the Python 3.10+ standard library (zero external dependencies)
- [ ] Avoids `eval`, `exec`, `os.system`, `pickle`, and `subprocess(..., shell=True)`
- [ ] Validates all file paths and network targets safely
- [ ] Includes unit tests in `tests/`