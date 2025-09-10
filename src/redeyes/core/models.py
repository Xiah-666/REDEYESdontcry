#!/usr/bin/env python3
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class TestPhase(Enum):
    OSINT = "osint"
    RECONNAISSANCE = "reconnaissance"
    ENUMERATION = "enumeration"
    VULNERABILITY_SCAN = "vulnerability_scan"
    EXPLOITATION = "exploitation"
    POST_EXPLOITATION = "post_exploitation"
    PERSISTENCE = "persistence"
    LOG_ANALYSIS = "log_analysis"
    REPORTING = "reporting"


@dataclass
class Target:
    ip: str
    hostname: Optional[str] = None
    open_ports: List[int] = field(default_factory=list)
    services: Dict[int, str] = field(default_factory=dict)
    vulnerabilities: List[str] = field(default_factory=list)
    exploited: bool = False
    shells: List[str] = field(default_factory=list)
    credentials: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)


@dataclass
class ChatMessage:
    sender: str  # 'user' or 'ai'
    content: str
    timestamp: datetime
    context_data: Optional[Dict] = None


@dataclass
class Case:
    """Represents an investigation case context.
    Outputs may be scoped under this root while the case is active.
    """
    case_id: str
    name: str
    root: Path
    created_at: datetime
    description: Optional[str] = None
    entities: List[Dict] = field(default_factory=list)  # persons/companies
    artifacts: List[Dict] = field(default_factory=list)  # files/intelligence
    notes: List[str] = field(default_factory=list)
    status: str = "open"  # open/closed

