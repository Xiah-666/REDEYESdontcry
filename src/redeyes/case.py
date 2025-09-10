#!/usr/bin/env python3
from __future__ import annotations
import json
import os
import shutil
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class Entity:
    id: str
    kind: str  # 'person' | 'company'
    name: str
    identifiers: Dict[str, str] = field(default_factory=dict)
    emails: List[str] = field(default_factory=list)
    phones: List[str] = field(default_factory=list)
    usernames: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)


@dataclass
class Artifact:
    id: str
    type: str
    path: str
    sha256: Optional[str] = None
    acquired_at: str = field(default_factory=lambda: datetime.now().isoformat())
    source: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    notes: Optional[str] = None


@dataclass
class Case:
    id: str
    name: str
    root_dir: str
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    closed_at: Optional[str] = None
    entities: List[Entity] = field(default_factory=list)
    artifacts: List[Artifact] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)

    def save(self) -> None:
        root = Path(self.root_dir)
        root.mkdir(parents=True, exist_ok=True)
        (root / "entities").mkdir(exist_ok=True)
        (root / "artifacts").mkdir(exist_ok=True)
        (root / "evidence").mkdir(exist_ok=True)
        (root / "reports").mkdir(exist_ok=True)
        (root / "dossier").mkdir(exist_ok=True)
        (root / "logs").mkdir(exist_ok=True)
        (root / "chain_of_custody.jsonl").touch(exist_ok=True)
        with open(root / "case.json", "w") as f:
            json.dump(asdict(self), f, indent=2)


class CaseManager:
    def __init__(self, base_dir: Optional[str] = None):
        self.base_dir = Path(base_dir or os.path.expanduser("~/redeyes_cases"))
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.active: Optional[Case] = None

    def list_cases(self) -> List[Case]:
        cases: List[Case] = []
        for d in sorted(self.base_dir.glob("*/case.json")):
            try:
                data = json.loads(d.read_text())
                cases.append(Case(**data))
            except Exception:
                continue
        return cases

    def _slugify(self, name: str) -> str:
        s = "".join(ch.lower() if ch.isalnum() else "_" for ch in name).strip("_")
        while "__" in s:
            s = s.replace("__", "_")
        return s or "case"

    def create_case(self, name: str) -> Case:
        cid = datetime.now().strftime("%Y%m%d_%H%M%S")
        slug = self._slugify(name)
        root = self.base_dir / f"{cid}_{slug}"
        case = Case(id=cid, name=name, root_dir=str(root))
        case.save()
        self.active = case
        return case

    def open_case(self, root_dir: str) -> Case:
        case_file = Path(root_dir) / "case.json"
        data = json.loads(case_file.read_text())
        self.active = Case(**data)
        return self.active

    def close_case(self) -> None:
        if not self.active:
            return
        self.active.closed_at = datetime.now().isoformat()
        self.active.save()
        self.active = None

    def export_active(self, out_zip_path: str) -> str:
        if not self.active:
            raise RuntimeError("No active case")
        root = Path(self.active.root_dir)
        base = str(root)
        archive = shutil.make_archive(out_zip_path, 'zip', base_dir=base)
        return archive

    def promote_to_evidence(self, src_path: str, source: Optional[str] = None, tags: Optional[List[str]] = None, notes: Optional[str] = None) -> Dict:
        if not self.active:
            raise RuntimeError("No active case")
        import hashlib
        p = Path(src_path)
        if not p.exists():
            raise FileNotFoundError(str(p))
        data = p.read_bytes()
        sha = hashlib.sha256(data).hexdigest()
        ev_id = f"ev_{int(time.time())}"
        dest = Path(self.active.root_dir) / "evidence" / f"{ev_id}_{p.name}"
        dest.write_bytes(data)
        entry = {
            "id": ev_id,
            "timestamp": datetime.now().isoformat(),
            "original_path": str(p),
            "stored_path": str(dest),
            "sha256": sha,
            "source": source,
            "tags": tags or [],
            "notes": notes or "",
        }
        with open(Path(self.active.root_dir) / "chain_of_custody.jsonl", "a") as f:
            f.write(json.dumps(entry) + "\n")
        # Track in artifacts list
        art = Artifact(id=ev_id, type="evidence", path=str(dest), sha256=sha, source=source, tags=tags or [], notes=notes)
        self.active.artifacts.append(art)
        self.active.save()
        return entry

