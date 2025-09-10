#!/usr/bin/env python3
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional

# Heuristic + LLM-backed tips generator

def _heuristic_tips(ctx: Dict) -> List[str]:
    tips: List[str] = []
    phase = ctx.get("phase", "").lower()
    services: Dict[int, str] = ctx.get("services", {})
    open_ports = sorted([int(p) for p in ctx.get("open_ports", [])])
    tools = ctx.get("tools", {})

    if phase in ("osint", "reconnaissance"):
        # Domain tips
        if ctx.get("domain"):
            tips.append("Query CT logs via crt.sh and pivot to subdomain enum with amass/subfinder if present.")
            if tools.get("amass", {}).get("available"):
                tips.append("Run passive amass enum: amass enum -passive -d <domain>")
            if tools.get("subfinder", {}).get("available"):
                tips.append("Run subfinder: subfinder -d <domain> -silent")
        # Emails present
        if ctx.get("emails"):
            if tools.get("holehe", {}).get("available"):
                tips.append("Check email exposure with holehe (read-only): holehe -s <email>")
            tips.append("Search paste sites for email leaks (psbdmp) and GitHub code search.")
    if open_ports:
        if 80 in open_ports or 443 in open_ports:
            if tools.get("whatweb", {}).get("available"):
                tips.append("Fingerprint web tech (whatweb) and enumerate dirs with gobuster.")
            else:
                tips.append("Probe HTTP banners and dirs (curl + common wordlists).")
        if 22 in open_ports:
            tips.append("Collect SSH banner and supported algorithms; avoid brute force unless in scope.")
        if any(p in open_ports for p in (139, 445)):
            tips.append("Run safe SMB NSE scripts and enum4linux; check signing and guest access.")
        if 161 in open_ports:
            tips.append("Test SNMP v1/v2 RO strings with onesixtyone; enumerate with snmpwalk (authorized only).")
    if not tips:
        tips.append("Review current artifacts and consolidate findings into the case dossier.")
    return tips[:7]


def get_tips(ctx: Dict, framework=None) -> List[str]:
    """Return prioritized tips using LLM if available, otherwise heuristics."""
    try:
        if framework and getattr(framework, "selected_model", None):
            # Prefer Baron-like models for advice
            sys_prompt = (
                "You are a seasoned penetration tester. Provide concise, actionable next steps. "
                "Avoid destructive actions. Always respect scope and legality."
            )
            # Compact context
            summary = {
                "phase": ctx.get("phase"),
                "target": ctx.get("target"),
                "domain": ctx.get("domain"),
                "open_ports": ctx.get("open_ports", [])[:20],
                "notable_services": {str(k): v for k, v in list(ctx.get("services", {}).items())[:10]},
                "tools_available": [k for k, v in ctx.get("tools", {}).items() if v.get("available")][:15],
            }
            prompt = (
                "Given this context, list 5-7 short prioritized next steps (numbered).\n" +
                str(summary)
            )
            out = framework.query_ollama(prompt, system_prompt=sys_prompt)
            # Extract numbered lines if present
            tips = []
            for line in out.splitlines():
                s = line.strip()
                if not s:
                    continue
                if s[0].isdigit() or s.startswith("- "):
                    tips.append(s.lstrip("- "))
            if tips:
                return tips[:7]
        # Fallback
        return _heuristic_tips(ctx)
    except Exception:
        return _heuristic_tips(ctx)

