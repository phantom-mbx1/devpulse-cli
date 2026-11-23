# ⚡ DevPulse CLI

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square)
![Dependencies](https://img.shields.io/badge/Dependencies-Zero-brightgreen?style=flat-square)
![Security](https://img.shields.io/badge/Security-AST%20Hardened-critical?style=flat-square)
![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-orange?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-lightgrey?style=flat-square)

A hardened, **zero-dependency** command-line toolkit for auditing local development environments, open ports, Git secret leaks, TLS certificates, .env parity, and system telemetry.

---

## 🛡️ Security-First Design
- **Zero External Packages:** 100% Python standard library — eliminates third-party supply-chain risk.
- **AST Static Gatekeeper:** Every plugin is inspected via Python's st module before loading, blocking eval, exec, pickle, os.system, and shell=True.
- **Loopback Protection:** Port scanning defaults strictly to 127.0.0.1 unless --allow-remote is explicitly specified.
- **Cross-Platform CI:** Automated unit and security boundary tests run on Linux, Windows, and macOS on every Pull Request.

---

## 🚀 Quick Start

```bash
git clone [https://github.com/](https://github.com/)phantom-mbx1/devpulse-cli.git
cd devpulse-cli

# 1. Concurrently scan local dev & database ports
python devpulse.py port_audit

# 2. Audit Git repo hygiene, oversized files & accidental secret leaks
python devpulse.py git_health

# 3. Check DNS latency, TCP speed & SSL certificate expiry days
python devpulse.py net_diag

# 4. Verify .env is gitignored and matches .env.example keys
python devpulse.py env_guard

# 5. Inspect OS, Python runtime, CPU cores & disk capacity
python devpulse.py sys_pulse
```

---

## 🧩 Built-In Modules

| Module | Purpose |
| :--- | :--- |
| port_audit | Concurrent loopback scanner for common web & database ports (3000, 5173, 8000, 3306, 5432, 6379, etc.) |
| git_health | Detects uncommitted changes, unpushed commits, oversized files, and hardcoded API keys/private keys |
| 
et_diag | Measures DNS resolution, TCP handshake time, and TLS certificate expiration days |
| env_guard | Audits .gitignore rules for .env exposure and checks key parity with .env.example without printing secrets |
| sys_pulse | Displays cross-platform OS, logical CPU count, Python executable path, and free disk space |

---

## 🤝 Contribute a Plugin
Want to add a new diagnostic module? Read [CONTRIBUTING.md](CONTRIBUTING.md) and submit a PR — new plugins take under 3 minutes to build!
