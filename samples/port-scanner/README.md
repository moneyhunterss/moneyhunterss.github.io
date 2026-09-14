# Port Scanner

Concurrent TCP port scanner built in pure Python (stdlib only — zero deps).

## Features

- Concurrent scanning (100 workers by default, configurable)
- Service identification (IANA well-known ports)
- Flexible port specification (`1-1024` or `22,80,443`)
- Per-port timeout (default 1.5s)
- Open-only filter mode

## Quick start

```bash
# Scan default ports (1-1024) on a host
python portscanner.py --target scanme.nmap.org

# Scan specific ports
python portscanner.py --target 10.0.0.5 --ports 22,80,443,8080

# Full range scan with 200 workers
python portscanner.py --target 192.168.1.1 --ports 1-65535 --workers 200

# Show only open ports
python portscanner.py --target scanme.nmap.org --open-only
```

## Example output

```
Scanning scanme.nmap.org on 1024 ports (100 workers)...

PORT       STATE     SERVICE
----------------------------------
22         open      ssh
80         open      http

2 open ports found on scanme.nmap.org
```

## Use cases

- Security audit of your own infrastructure
- Network inventory (find what's exposed)
- Service discovery on local network
- Pre-pentest recon (with permission!)

## Tech

- Python 3.10+
- `socket` — TCP probe
- `concurrent.futures.ThreadPoolExecutor` — parallel workers
- Zero external dependencies

## Legal

Only scan hosts you own or have explicit permission to scan. Port scanning
without consent is illegal in most jurisdictions. Use `scanme.nmap.org` for
testing (explicitly provided by Nmap for this purpose).

## License

MIT — for educational and authorized security testing only.
