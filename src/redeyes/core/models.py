#!/usr/bin/env python3
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
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

