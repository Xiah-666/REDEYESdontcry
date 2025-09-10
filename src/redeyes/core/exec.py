#!/usr/bin/env python3
from __future__ import annotations
import shlex
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Union


@dataclass
class ResultEnvelope:
    ok: bool
    stdout: str
    stderr: str
    exit_code: int
    duration_s: float
    truncated: bool
    log_path: Optional[Path] = None


CATastrophic_BLOCKS = [
    "rm -rf /",
    "mkfs",
    ":(){:|:&};:",  # fork bomb
    "dd if=/dev/zero",
    "> /dev/sd",
    "shred /",
]


def _looks_catastrophic(cmd: str) -> bool:
    low = cmd.lower()
    for pat in CATastrophic_BLOCKS:
        if pat in low:
            return True
    return False


def safe_run(
    command: Union[str, List[str]],
    *,
    cwd: Optional[Union[str, Path]] = None,
    timeout_s: int = 600,
    env: Optional[dict] = None,
    output_file: Optional[Union[str, Path]] = None,
    max_output_kb: int = 2048,
) -> ResultEnvelope:
    """Run a command safely with timeout, truncation, and minimal catastrophic blocks.
    Returns a ResultEnvelope with stdout/stderr and metadata.
    """
    if isinstance(command, list):
        cmd_str = " ".join(shlex.quote(c) for c in command)
        shell = False
        cmd = command
    else:
        cmd_str = command
        shell = True
        cmd = command

    if _looks_catastrophic(cmd_str):
        return ResultEnvelope(
            ok=False,
            stdout="",
            stderr="Blocked catastrophic pattern in command",
            exit_code=126,
            duration_s=0.0,
            truncated=False,
        )

    start = time.time()
    try:
        proc = subprocess.run(
            cmd,
            shell=shell,
            capture_output=True,
            text=True,
            timeout=timeout_s,
            cwd=str(cwd) if cwd else None,
            env=env,
        )
        duration = time.time() - start
        out = proc.stdout or ""
        err = proc.stderr or ""
        truncated = False
        limit = max_output_kb * 1024
        if len(out) > limit:
            out = out[:limit] + "\n[...truncated...]\n"
            truncated = True
        if output_file:
            p = Path(output_file)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(out + ("\n[stderr]\n" + err if err else ""))
            log_path = p
        else:
            log_path = None
        return ResultEnvelope(
            ok=proc.returncode == 0,
            stdout=out,
            stderr=err,
            exit_code=proc.returncode,
            duration_s=duration,
            truncated=truncated,
            log_path=log_path,
        )
    except subprocess.TimeoutExpired:
        duration = time.time() - start
        return ResultEnvelope(
            ok=False,
            stdout="",
            stderr=f"Command timed out after {timeout_s}s",
            exit_code=124,
            duration_s=duration,
            truncated=False,
        )

