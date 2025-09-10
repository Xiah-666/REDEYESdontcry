#!/usr/bin/env python3
from __future__ import annotations
import subprocess
from contextlib import contextmanager
from typing import Optional


def _which(bin_name: str) -> Optional[str]:
    try:
        import shutil
        return shutil.which(bin_name)
    except Exception:
        return None


def detect_macchanger() -> bool:
    return _which("macchanger") is not None


def get_current_mac(interface: str) -> Optional[str]:
    try:
        out = subprocess.run(["ip", "link", "show", interface], capture_output=True, text=True, timeout=5)
        if out.returncode == 0:
            for line in out.stdout.split("\n"):
                line = line.strip()
                if line.startswith("link/") and len(line.split()) >= 2:
                    return line.split()[1]
    except Exception:
        pass
    return None


def spoof_mac_random(interface: str) -> Optional[str]:
    try:
        subprocess.run(["sudo", "ip", "link", "set", interface, "down"], timeout=5)
        res = subprocess.run(["sudo", "macchanger", "-r", interface], capture_output=True, text=True, timeout=10)
        subprocess.run(["sudo", "ip", "link", "set", interface, "up"], timeout=5)
        if res.returncode == 0:
            # Try to parse new MAC from macchanger output
            for line in res.stdout.split("\n"):
                if "New MAC" in line or "New MAC" in res.stderr:
                    parts = line.split()
                    for token in parts:
                        if ":" in token and len(token) >= 11:
                            return token
        # Fallback: read from ip link
        return get_current_mac(interface)
    except Exception:
        return None


def restore_mac_permanent(interface: str) -> bool:
    try:
        subprocess.run(["sudo", "ip", "link", "set", interface, "down"], timeout=5)
        res = subprocess.run(["sudo", "macchanger", "-p", interface], capture_output=True, text=True, timeout=10)
        subprocess.run(["sudo", "ip", "link", "set", interface, "up"], timeout=5)
        return res.returncode == 0
    except Exception:
        return False


@contextmanager
def mac_spoof_ctx(interface: str):
    """Context manager that spoofs MAC on entry and restores on exit."""
    old_mac = get_current_mac(interface)
    try:
        spoof_mac_random(interface)
        yield
    finally:
        if old_mac:
            restore_mac_permanent(interface)

