# Security Policy

## Supported Versions
| Version | Supported |
| :--- | :--- |
| 2.0.x | Yes |
| < 2.0 | No |

## Architectural Security Guarantees
- **Zero Third-Party Dependencies:** Eliminates supply-chain compromise from external packages.
- **Static AST Plugin Gatekeeper:** Blocks `eval`, `exec`, `os.system`, `pickle`, and `shell=True` before loading plugins.
- **Loopback Scan Default:** Network scanning defaults strictly to `127.0.0.1` unless `--allow-remote` is explicitly passed.

## Reporting a Vulnerability
Please report suspected vulnerabilities privately via GitHub Security Advisories rather than opening a public issue.