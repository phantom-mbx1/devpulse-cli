from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import ipaddress
import socket

DESCRIPTION = "Concurrently scan local development & database ports with IP safety validation"

COMMON_DEV_PORTS: dict[int, str] = {
    22: "SSH",
    80: "HTTP",
    443: "HTTPS",
    3000: "Node / React / Next.js",
    3306: "MySQL / MariaDB",
    4200: "Angular",
    5000: "Flask / Python / AirPlay",
    5173: "Vite",
    5432: "PostgreSQL",
    6379: "Redis",
    8000: "Django / FastAPI",
    8080: "HTTP Alt / Spring / Tomcat",
    8443: "HTTPS Alt",
    9000: "PHP-FPM / SonarQube",
    27017: "MongoDB",
}


def _validate_target_ip(host: str, allow_remote: bool) -> str:
    try:
        ip_obj = ipaddress.ip_address(host)
    except ValueError as exc:
        raise ValueError(f"Invalid IP address '{host}'. Provide a valid IPv4/IPv6 address.") from exc

    if not ip_obj.is_loopback and not allow_remote:
        raise ValueError(
            f"Refusing to scan non-loopback address '{host}' without '--allow-remote' flag."
        )
    return str(ip_obj)


def _check_port(host: str, port: int, timeout: float) -> tuple[int, bool]:
    family = socket.AF_INET6 if ":" in host else socket.AF_INET
    with socket.socket(family, socket.SOCK_STREAM) as sock:
        sock.settimeout(timeout)
        is_open = sock.connect_ex((host, port)) == 0
        return port, is_open


def register(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--host", default="127.0.0.1", help="Target IP address (default: 127.0.0.1)")
    parser.add_argument("--timeout", type=float, default=0.25, help="Socket timeout in seconds (0.05 - 5.0)")
    parser.add_argument(
        "--allow-remote",
        action="store_true",
        help="Explicitly permit scanning non-loopback IP addresses you own",
    )


def run(args: argparse.Namespace) -> int:
    if not (0.05 <= args.timeout <= 5.0):
        print("[ERROR] Timeout must be between 0.05 and 5.0 seconds.")
        return 1

    try:
        target_ip = _validate_target_ip(args.host, args.allow_remote)
    except ValueError as err:
        print(f"[SECURITY] {err}")
        return 1

    print(f"\nScanning {len(COMMON_DEV_PORTS)} common development ports on {target_ip}...\n")
    print(f"{'PORT':<8} {'STATE':<10} {'TYPICAL SERVICE'}")
    print("-" * 48)

    open_ports: list[int] = []
    with ThreadPoolExecutor(max_workers=16) as executor:
        futures = {
            executor.submit(_check_port, target_ip, port, args.timeout): port
            for port in COMMON_DEV_PORTS
        }
        for future in as_completed(futures):
            port, is_open = future.result()
            if is_open:
                open_ports.append(port)

    for port in sorted(open_ports):
        print(f"{port:<8} {'OPEN':<10} {COMMON_DEV_PORTS[port]}")

    if not open_ports:
        print("No common development ports are actively listening.")
    print(f"\nSummary: {len(open_ports)} open / {len(COMMON_DEV_PORTS)} checked.\n")
    return 0