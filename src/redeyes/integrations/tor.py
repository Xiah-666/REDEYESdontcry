#!/usr/bin/env python3
from __future__ import annotations
import os
import subprocess
from typing import List, Optional, Union


def detect_tor() -> bool:
    return shutil_which("tor") is not None


def detect_torsocks() -> bool:
    return shutil_which("torsocks") is not None or shutil_which("torify") is not None


def shutil_which(bin_name: str) -> Optional[str]:
    try:
        import shutil
        return shutil.which(bin_name)
    except Exception:
        return None


def start_tor() -> bool:
    # Try systemctl, then service
    try:
        subprocess.run(["systemctl", "start", "tor"], timeout=10)
        return True
    except Exception:
        pass
    try:
        subprocess.run(["sudo", "service", "tor", "start"], timeout=10)
        return True
    except Exception:
        return False


def stop_tor() -> bool:
    try:
        subprocess.run(["systemctl", "stop", "tor"], timeout=10)
        return True
    except Exception:
        pass
    try:
        subprocess.run(["sudo", "service", "tor", "stop"], timeout=10)
        return True
    except Exception:
        return False


def wrap_with_tor(command: Union[List[str], str]) -> Union[List[str], str]:
    """Wrap command with torsocks/torify if available."""
    sock = shutil_which("torsocks") or shutil_which("torify")
    if not sock:
        return command
    if isinstance(command, list):
        return [sock] + command
    return f"{sock} {command}"


def verify_exit_ip(timeout: int = 15) -> Optional[str]:
    """Return text of exit IP info via Tor, or None."""
    curl = shutil_which("curl")
    if not curl:
        return None
    cmd = wrap_with_tor([curl, "-sS", "https://check.torproject.org/api/ip"])
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return out.stdout.strip() if out.returncode == 0 else None
    except Exception:
        return None

