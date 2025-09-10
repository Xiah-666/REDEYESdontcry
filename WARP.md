# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

Repository: REDEYESdontcry (Python, src-layout package + legacy TUI)

Common commands (local dev)
- Python version: 3.11 (see .github/workflows/ci.yml)
- Create venv and install (editable + dev tools)
  - python -m venv .venv && source .venv/bin/activate
  - python -m pip install --upgrade pip
  - pip install -e .[dev]
- Lint (matches CI)
  - black --check .
  - flake8 .
- Test suite
  - pytest -q
- Run a single test
  - pytest -q tests/test_safe_run.py::test_safe_run_echo
- Build a distribution (optional)
  - python -m pip install --upgrade build
  - python -m build

Run the app
- CLI wrapper (preferred, installed by entry point)
  - redeyes [--check] [--no-art] [-y|--assume-yes] [--results-dir DIR] [--model NAME] [--log-level LEVEL] [--intensity 0..2]
- Legacy TUI (direct)
  - ./REDEYESdontcry.py
- Preflight environment/tool check (non-interactive summary)
  - redeyes --check
- Tool inventory and install hinting (inside the TUI)
  - Main Menu → 10 “Tool Status” → shows available/missing tools and suggests a sudo apt install command for common gaps

AI and autonomous operations
- Local LLM via Ollama is optional but unlocks Chat and Autonomous Agent.
  - Ensure Ollama is running and at least one model is available: ollama list
  - You can pull a lighter model if needed, e.g.: ollama pull wizard-vicuna-uncensored:7b
  - Start the app and open the agent: redeyes → option 8 “AUTONOMOUS AI AGENT”
  - Model selection and supervised execution are built-in (confirmation prompts before risky actions).
- Useful environment knobs for AI/model selection (also settable via CLI flags):
  - OLLAMA_HOST, OLLAMA_PORT, OLLAMA_MMAP (see README)
  - REDEYES_MODEL (preferred model name)
  - REDEYES_ASSUME_YES=1 to auto-acknowledge the legal banner

Environment variables and outputs
- Results directory (default): /tmp/redeyesdontcry_YYYYMMDD_HHMMSS/
  - Can override via: REDEYES_RESULTS_DIR or --results-dir
- Logging level: REDEYES_LOG_LEVEL (e.g., INFO, DEBUG)
- Art/UX toggles: REDEYES_NO_ART=1, REDEYES_ART_INTENSITY=0..2
- Check-mode sentinel (used by --check path): REDEYES_CHECK_MODE=1
- Ollama-related: OLLAMA_* variables as above
- Outputs include command transcripts, tool outputs, reports (HTML/MD/JSON), chat logs

External tools and free-API integrations
- Tool detection happens at startup (REDEYESdontcry.py → detect_tools()). Key categories:
  - Recon: nmap, masscan, zmap, dnsrecon, fierce, amass, subfinder
  - Web: nikto, gobuster, dirb, whatweb, wpscan, sqlmap
  - OSINT: theHarvester, recon-ng, maltego, shodan, assetfinder, httprobe
  - Services: enum4linux, smbclient, nbtscan, onesixtyone, snmpwalk
  - Exploitation: metasploit (msfconsole), hydra, john, hashcat, burpsuite
- To expand the toolset (including geo/private/public intel): edit the tools map in REDEYESdontcry.py:detect_tools() to add new binaries. Use redeyes --check to verify detection.
- Built-in OSINT modules call free/CLI-first paths when possible:
  - Shodan CLI (requires free API key init via: shodan init {{SHODAN_API_KEY}})
  - theHarvester supports multiple public sources
  - Individual OSINT module includes a HaveIBeenPwned check path; some providers require API keys and rate limits (configure externally)

Supervised “full network test” via the agent
- Start the app, then: option 8 → pick an Ollama model → choose an operation:
  - Full autonomous red team (with explicit confirmations)
  - Autonomous OSINT / Enumeration / Vulnerability phases
- Safety:
  - Central execution goes through redeyes.core.exec.safe_run where available (timeouts, output truncation, simple catastrophic command blocks).
  - The agent adds confirm prompts and rate limits; exploitation flows require explicit user confirmation.

Architecture (big picture)
- Entry points
  - src/redeyes/cli.py → parses flags, syncs env, instantiates REDEYESFramework from legacy REDEYESdontcry.py
  - Console TUI and menus are implemented in REDEYESdontcry.py (Rich + art_assets.py banners)
- Core domain
  - src/redeyes/core/models.py defines TestPhase, Target, ChatMessage
  - src/redeyes/core/exec.py provides safe_run(ResultEnvelope) used by agent/executors
- Feature modules
  - ai_agent.py: autonomous planning/execution, command extraction, supervised runs, msf resource-file driver
  - redeyes_implementations.py: concrete workflows for OSINT, enumeration, vuln scanning, SMB, etc.
  - individual_osint.py: person-focused OSINT (social/email/breach stubs + report generation)
  - wireless_pentest.py: WiFi workflows (monitor mode, airodump/aircrack/reaver flows, reporting)
- Data/outputs
  - Session-scoped results dir under /tmp; HTML/MD/JSON reports synthesized from session data
- AI integration
  - Ollama model discovery and auto-selection (prefers certain uncensored models if present)

CI reference
- .github/workflows/ci.yml uses Python 3.11 and runs:
  - pip install -e .[dev]
  - black --check . && flake8 .
  - pytest -q
- Keep local lint/test commands aligned with CI for consistent results.

Notes for extending tools and free APIs
- Prefer CLI-first integrations to keep secrets out of code. For API-based OSINT, wire providers via environment variables and initialize their CLIs (e.g., shodan init {{SHODAN_API_KEY}}).
- To add new recon/exploitation tools, put the binary name in detect_tools() so it’s surfaced in Tool Status and available to agent planning.
- The agent will attempt to extract and propose commands; users remain in the loop for confirmation before execution.
