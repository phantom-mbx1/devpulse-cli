from __future__ import annotations

import argparse
from datetime import datetime, timezone
import socket
import ssl
import time

DESCRIPTION = "Measure DNS latency, TCP/TLS handshake speed, and SSL certificate expiry"

DEFAULT_TARGETS = [
    "github.com",
    "pypi.org",
    "registry.npmjs.org",
]


def register(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--hosts",
        nargs="+",
        default=DEFAULT_TARGETS,
        help="List of HTTPS hostnames to inspect (default: github.com pypi.org registry.npmjs.org)",
    )
    parser.add_argument("--timeout", type=float, default=3.0, help="Connection timeout in seconds")


def _inspect_host(host: str, timeout: float) -> tuple[str, str, str, str]:
    context = ssl.create_default_context()
    try:
        t0 = time.perf_counter()
        addr_info = socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)
        dns_ms = (time.perf_counter() - t0) * 1000
        ip = addr_info[0][4][0]

        t1 = time.perf_counter()
        with socket.create_connection((ip, 443), timeout=timeout) as raw_sock:
            tcp_ms = (time.perf_counter() - t1) * 1000
            with context.wrap_socket(raw_sock, server_hostname=host) as tls_sock:
                cert = tls_sock.getpeercert()
                not_after = cert.get("notAfter", "")
                expiry_dt = datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)
                days_left = (expiry_dt - datetime.now(timezone.utc)).days
                return f"{dns_ms:.1f}", f"{tcp_ms:.1f}", f"{days_left}d", "OK"
    except ssl.SSLCertVerificationError:
        return "--", "--", "INVALID", "TLS ERROR"
    except Exception:
        return "--", "--", "--", "UNREACHABLE"


def run(args: argparse.Namespace) -> int:
    if not (0.5 <= args.timeout <= 15.0):
        print("[ERROR] Timeout must be between 0.5 and 15.0 seconds.")
        return 1

    print("\nNetwork & TLS Certificate Audit")
    print("-" * 68)
    print(f"{'HOSTNAME':<26} {'DNS (ms)':<11} {'TCP (ms)':<11} {'CERT EXP':<10} {'STATUS'}")
    print("-" * 68)

    for host in args.hosts[:15]:  # Cap at 15 hosts per run
        dns_s, tcp_s, exp_s, status = _inspect_host(host.strip(), args.timeout)
        print(f"{host:<26} {dns_s:<11} {tcp_s:<11} {exp_s:<10} {status}")
    print()
    return 0