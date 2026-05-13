#!/usr/bin/env python3
"""
Installs (or updates) the 5 AM Mountain Time cron job for morning_digest.py.

  python3 /home/user/ClaudeRoutines/install_cron.py

MDT (UTC-6): 5:00 AM MDT = 11:00 AM UTC → cron: 0 11 * * *
MST (UTC-7): 5:00 AM MST = 12:00 PM UTC → cron: 0 12 * * *

The script reads TIMEZONE_OFFSET from ~/.claude/morning_digest.env to pick
the right UTC hour automatically.
"""

import os
import subprocess
import sys

SCRIPT = "/home/user/ClaudeRoutines/morning_digest.py"
LOG = "/home/user/ClaudeRoutines/morning_digest.log"
ENV_FILE = os.path.expanduser("~/.claude/morning_digest.env")
MARKER = "# morning_digest_cron"


def _read_tz_offset() -> str:
    try:
        with open(ENV_FILE) as f:
            for line in f:
                if line.startswith("TIMEZONE_OFFSET="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    except FileNotFoundError:
        pass
    return "-06:00"  # default MDT


def _tz_to_utc_hour(tz_offset: str) -> int:
    """5 AM local → UTC hour."""
    sign = 1 if tz_offset[0] == "+" else -1
    h = int(tz_offset.lstrip("+-").split(":")[0])
    local_hour = 5
    utc_hour = (local_hour - sign * h) % 24
    return utc_hour


def main() -> None:
    tz_offset = _read_tz_offset()
    utc_hour = _tz_to_utc_hour(tz_offset)

    python = sys.executable
    cron_line = (
        f"0 {utc_hour} * * * "
        f"{python} {SCRIPT} >> {LOG} 2>&1 "
        f"{MARKER}"
    )

    # Read current crontab, strip any existing entry, append new one
    result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
    existing = result.stdout if result.returncode == 0 else ""
    lines = [ln for ln in existing.splitlines() if MARKER not in ln]
    lines.append(cron_line)
    new_crontab = "\n".join(lines) + "\n"

    proc = subprocess.run(["crontab", "-"], input=new_crontab, text=True)
    if proc.returncode != 0:
        sys.exit("Failed to install cron job.")

    print(f"✓ Cron job installed (runs at {utc_hour:02d}:00 UTC = 5:00 AM {tz_offset}).")
    print(f"  Log file: {LOG}")
    print(f"\nVerify with:  crontab -l")
    print(f"Test now  :  python3 {SCRIPT}")


if __name__ == "__main__":
    main()
