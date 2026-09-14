#!/usr/bin/env python3
"""watchdir — file watcher with regex triggers.

Watches a directory for new files matching a regex, runs a command.
Like a poor-man's inotify + cron, useful for:
- Auto-process uploaded files
- Auto-run tests on file change
- Auto-deploy on git push
- Build pipelines

Usage:
    python watchdir.py ./input '.*\.csv$' 'process.sh {}'
    python watchdir.py ./uploads '(?i)\.(jpg|png)$' 'python resize.py {}'
"""
from __future__ import annotations
import argparse
import logging
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Callable

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("watchdir")


class FileWatcher:
    """Watch a directory for new files matching a regex pattern."""

    def __init__(self, directory: str, pattern: str, callback: Callable[[Path], None], poll_interval: float = 1.0):
        self.directory = Path(directory)
        self.pattern = re.compile(pattern)
        self.callback = callback
        self.poll_interval = poll_interval
        self.seen: set[Path] = set()

        if not self.directory.exists():
            raise FileNotFoundError(f"Directory not found: {self.directory}")
        if not self.directory.is_dir():
            raise NotADirectoryError(f"Not a directory: {self.directory}")

    def scan(self) -> list[Path]:
        """Find new files matching pattern that haven't been seen."""
        new_files = []
        for entry in self.directory.rglob("*"):
            if not entry.is_file():
                continue
            if entry in self.seen:
                continue
            if self.pattern.search(entry.name):
                self.seen.add(entry)
                new_files.append(entry)
        return new_files

    def run(self):
        """Main watch loop."""
        log.info(f"watching {self.directory} for /{self.pattern.pattern}/")
        # Initial scan — don't trigger callback for files that existed before
        for entry in self.directory.rglob("*"):
            if entry.is_file():
                self.seen.add(entry)
        log.info(f"  initial scan: {len(self.seen)} existing files ignored")

        try:
            while True:
                new_files = self.scan()
                for f in new_files:
                    log.info(f"  NEW: {f}")
                    try:
                        self.callback(f)
                    except Exception as e:
                        log.error(f"  callback error on {f}: {e}")
                time.sleep(self.poll_interval)
        except KeyboardInterrupt:
            log.info("stopping")


def run_command(file_path: Path, command_template: str):
    """Run a shell command with file path substituted via {}."""
    cmd = command_template.replace("{}", str(file_path))
    log.info(f"  running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        log.error(f"  exit code {result.returncode}: {result.stderr}")
    else:
        log.info(f"  done")


def main():
    ap = argparse.ArgumentParser(description="Directory watcher with regex triggers")
    ap.add_argument("directory", help="directory to watch")
    ap.add_argument("pattern", help="regex pattern for files to match")
    ap.add_argument("command", help='command to run (use {} as file path placeholder, e.g. "process.sh {}")')
    ap.add_argument("--interval", "-i", type=float, default=1.0, help="poll interval in seconds")
    args = ap.parse_args()

    def callback(file_path: Path):
        run_command(file_path, args.command)

    watcher = FileWatcher(args.directory, args.pattern, callback, args.interval)
    watcher.run()


if __name__ == "__main__":
    main()
