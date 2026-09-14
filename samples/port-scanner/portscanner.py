#!/usr/bin/env python3
"""Port scanner — concurrent TCP port scanner.

Scans a target host for open TCP ports. Uses concurrent workers for speed.
Identifies common services by port number.

Usage:
    python portscanner.py --target 127.0.0.1
    python portscanner.py --target scanme.nmap.org --ports 1-1000
    python portscanner.py --target 10.0.0.5 --ports 22,80,443,8080
"""
from __future__ import annotations
import argparse
import socket
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import List

# Common service map (IANA well-known ports subset)
SERVICES = {
    21: "ftp", 22: "ssh", 23: "telnet", 25: "smtp", 53: "dns",
    80: "http", 110: "pop3", 143: "imap", 443: "https", 445: "smb",
    993: "imaps", 995: "pop3s", 1433: "mssql", 1521: "oracle",
    3306: "mysql", 3389: "rdp", 5432: "postgres", 5900: "vnc",
    6379: "redis", 8080: "http-alt", 8443: "https-alt", 9200: "elasticsearch",
    27017: "mongodb", 11211: "memcached",
}


@dataclass
class PortResult:
    port: int
    open: bool
    service: str = ""


def scan_port(host: str, port: int, timeout: float = 1.5) -> PortResult:
    """Scan a single TCP port. Returns PortResult."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            result = s.connect_ex((host, port))
            if result == 0:
                return PortResult(port=port, open=True, service=SERVICES.get(port, "?"))
    except (socket.gaierror, socket.error):
        pass
    return PortResult(port=port, open=False)


def parse_ports(ports_str: str) -> List[int]:
    """Parse port string: '1-1000' or '22,80,443' or '80'."""
    ports = set()
    for part in ports_str.split(","):
        part = part.strip()
        if "-" in part:
            start, end = part.split("-", 1)
            ports.update(range(int(start), int(end) + 1))
        else:
            ports.add(int(part))
    return sorted(ports)


def scan_host(host: str, ports: List[int], workers: int = 100, timeout: float = 1.5) -> List[PortResult]:
    """Scan host on given ports, concurrent."""
    results: List[PortResult] = []
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = {ex.submit(scan_port, host, p, timeout): p for p in ports}
        for future in as_completed(futures):
            results.append(future.result())
    return sorted(results, key=lambda r: r.port)


def main():
    ap = argparse.ArgumentParser(description="Concurrent TCP port scanner")
    ap.add_argument("--target", "-t", required=True, help="target host (IP or domain)")
    ap.add_argument("--ports", "-p", default="1-1024", help="ports (e.g. 1-1024 or 22,80,443)")
    ap.add_argument("--workers", "-w", type=int, default=100, help="concurrent workers (default 100)")
    ap.add_argument("--timeout", type=float, default=1.5, help="per-port timeout in seconds")
    ap.add_argument("--open-only", action="store_true", help="show only open ports")
    args = ap.parse_args()

    try:
        ports = parse_ports(args.ports)
    except ValueError:
        print("Error: invalid port specification. Use '1-1024' or '22,80,443'.", file=sys.stderr)
        sys.exit(1)

    print(f"Scanning {args.target} on {len(ports)} ports ({args.workers} workers)...\n")

    results = scan_host(args.target, ports, args.workers, args.timeout)

    open_results = [r for r in results if r.open]
    if args.open_only:
        displayed = open_results
    else:
        displayed = results

    print(f"{'PORT':<10}{'STATE':<10}{'SERVICE':<15}")
    print("-" * 35)
    for r in displayed:
        state = "open" if r.open else "closed"
        print(f"{r.port:<10}{state:<10}{r.service:<15}")

    print(f"\n{len(open_results)} open ports found on {args.target}")


if __name__ == "__main__":
    main()
