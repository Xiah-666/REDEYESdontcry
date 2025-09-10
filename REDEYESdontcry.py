#!/usr/bin/env python3
"""
REDEYESdontcry - Complete Advanced Red Team TUI Framework
Professional penetration testing suite with AI integration
Author: RedEyes Team
Compatible with: Kali Linux / Tsurugi Linux

Features:
- Beautiful TUI with Rich library
- Pink text for user, red for AI/agent responses
- Auto-detects and prioritizes uncensored/abliterated Ollama models
- Complete pentesting workflow from OSINT to reporting
- Context-aware AI assistant
- Professional tool integration
- Session management and logging
"""

import subprocess
import json
import sys
import os
import time
import socket
import threading
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import logging
from dataclasses import dataclass, field
from enum import Enum
import re
import xml.etree.ElementTree as ET
import signal
from concurrent.futures import ThreadPoolExecutor

# Rich TUI imports with auto-install
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    from rich.table import Table
    from rich.prompt import Prompt, Confirm
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
    from rich.syntax import Syntax
    from rich.align import Align
    from rich import box
    from rich.status import Status
except ImportError:
    print("🔄 Installing Rich TUI library...")
    subprocess.run([sys.executable, "-m", "pip", "install", "rich"], check=True)
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    from rich.table import Table
    from rich.prompt import Prompt, Confirm
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
    from rich.syntax import Syntax
    from rich.align import Align
    from rich import box
    from rich.status import Status

# Initialize Rich console
console = Console()

# Art themes for creepy banners on each screen
from art_assets import print_theme

# Color scheme - Pink for user, Red for AI/Agent
USER_COLOR = "bright_magenta"  # Pink for user
AI_COLOR = "red"               # Red for AI/Agent
SUCCESS_COLOR = "green"
WARNING_COLOR = "yellow"
ERROR_COLOR = "bright_red"
INFO_COLOR = "cyan"

# Ensure local 'src' is importable when running from repo root
try:
    from redeyes.core.models import TestPhase, Target, ChatMessage
except Exception:
    import sys as _sys
    from pathlib import Path as _Path
    _sys.path.insert(0, str((_Path(__file__).parent / "src").resolve()))
    from redeyes.core.models import TestPhase, Target, ChatMessage

class REDEYESFramework:
    def __init__(self):
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.results_dir = Path(f"/tmp/redeyesdontcry_{self.session_id}")
        self.results_dir.mkdir(exist_ok=True)

        # Core data
        self.targets = {}
        self.current_target = None
        self.current_phase = TestPhase.OSINT
        self.chat_history = []
        self.context_data = {}

        # Ollama integration
        self.ollama_models = []
        self.selected_model = None
        self.ollama_available = False

        # Tool status
        self.tools_status = {}
        self.scan_results = {}

        # Threading
        self.executor = ThreadPoolExecutor(max_workers=10)

        self.setup_logging()
        self.detect_tools()
        self.check_ollama()

    def setup_logging(self):
        """Setup comprehensive logging"""
        log_file = self.results_dir / f"redeyesdontcry_{self.session_id}.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"REDEYESdontcry session started: {self.session_id}")

    def detect_tools(self):
        """Detect available penetration testing tools"""
        tools = {
            # Network scanning
            'nmap': 'nmap',
            'masscan': 'masscan', 
            'zmap': 'zmap',

            # Web testing
            'nikto': 'nikto',
            'gobuster': 'gobuster',
            'dirb': 'dirb',
            'dirbuster': 'dirbuster',
            'whatweb': 'whatweb',
            'wafw00f': 'wafw00f',
            'wpscan': 'wpscan',
            'sqlmap': 'sqlmap',

            # Exploitation
            'metasploit': 'msfconsole',
            'armitage': 'armitage',
            'hydra': 'hydra',
            'john': 'john',
            'hashcat': 'hashcat',
            'burpsuite': 'burpsuite',

            # Network services
            'enum4linux': 'enum4linux',
            'smbclient': 'smbclient',
            'nbtscan': 'nbtscan',
            'onesixtyone': 'onesixtyone',
            'snmpwalk': 'snmpwalk',

            # OSINT
            'dnsrecon': 'dnsrecon',
            'fierce': 'fierce',
            'theharvester': 'theHarvester',
            'recon-ng': 'recon-ng',
            'maltego': 'maltego',
            'shodan': 'shodan',
            'amass': 'amass',
            'subfinder': 'subfinder',
            'assetfinder': 'assetfinder',
            'httprobe': 'httprobe',
            'waybackurls': 'waybackurls'
        }

        for tool_name, binary in tools.items():
            try:
                result = subprocess.run(['which', binary], 
                                      capture_output=True, text=True, timeout=5)
                self.tools_status[tool_name] = {
                    'available': result.returncode == 0,
                    'path': result.stdout.strip() if result.returncode == 0 else None
                }
            except Exception:
                self.tools_status[tool_name] = {'available': False, 'path': None}

    def check_ollama(self):
        """Check Ollama availability and get models"""
        try:
            result = subprocess.run(['ollama', 'list'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                self.ollama_available = True
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                for line in lines:
                    if line.strip():
                        model_name = line.split()[0]
                        self.ollama_models.append(model_name)

                # Auto-select best uncensored/abliterated model
                priority_keywords = [
                    'neuraldaredevil', 'daredevil', 'wizard-vicuna', 'dolphin',
                    'codellama', 'uncensored', 'abliterated', 'qwen', 'deepseek',
                    'lexi', 'chaos'
                ]

                for keyword in priority_keywords:
                    for model in self.ollama_models:
                        if keyword in model.lower():
                            self.selected_model = model
                            break
                    if self.selected_model:
                        break

                if not self.selected_model and self.ollama_models:
                    self.selected_model = self.ollama_models[0]

                self.logger.info(f"Ollama available with {len(self.ollama_models)} models")
                if self.selected_model:
                    self.logger.info(f"Selected AI model: {self.selected_model}")

        except Exception as e:
            self.ollama_available = False
            self.logger.warning(f"Ollama not available: {e}")

    def query_ollama(self, prompt: str, system_prompt: str = None) -> str:
        """Query Ollama model with context"""
        if not self.selected_model:
            return "AI not available - install Ollama and models"

        try:
            # Build context from current test data
            context = ""
            if self.current_target:
                target = self.targets.get(self.current_target)
                if target:
                    context = f"""
Current Target Context:
- IP: {target.ip}
- Hostname: {target.hostname or 'Unknown'}
- Open Ports: {target.open_ports[:10]}
- Services: {dict(list(target.services.items())[:5])}
- Vulnerabilities: {len(target.vulnerabilities)} found
- Phase: {self.current_phase.value}
"""

            if system_prompt:
                full_prompt = f"System: {system_prompt}\n\nContext: {context}\n\nUser: {prompt}"
            else:
                full_prompt = f"Context: {context}\n\nUser: {prompt}"

            cmd = ['ollama', 'run', self.selected_model]
            result = subprocess.run(cmd, input=full_prompt, capture_output=True, 
                                  text=True, timeout=120)

            response = result.stdout.strip()

            # Add to chat history
            self.chat_history.append(ChatMessage(
                sender='user',
                content=prompt,
                timestamp=datetime.now(),
                context_data=self.context_data.copy()
            ))

            self.chat_history.append(ChatMessage(
                sender='ai', 
                content=response,
                timestamp=datetime.now(),
                context_data=self.context_data.copy()
            ))

            return response

        except Exception as e:
            self.logger.error(f"Ollama query failed: {e}")
            return f"AI Error: {e}"

    def show_banner(self):
        """Display the main banner with disturbed art"""
        banner_text = """
██████╗ ███████╗██████╗ ███████╗██╗   ██╗███████╗███████╗
██╔══██╗██╔════╝██╔══██╗██╔════╝╚██╗ ██╔╝██╔════╝██╔════╝
██████╔╝█████╗  ██║  ██║█████╗   ╚████╔╝ █████╗  ███████╗
██╔══██╗██╔══╝  ██║  ██║██╔══╝    ╚██╔╝  ██╔══╝  ╚════██║
██║  ██║███████╗██████╔╝███████╗   ██║   ███████╗███████║
╚═╝  ╚═╝╚══════╝╚═════╝ ╚══════╝   ╚═╝   ╚══════╝╚══════╝
                    dontcry

🎯 Advanced Red Team Framework with AI Integration
🤖 Professional Penetration Testing Suite
        """

        disturbed_art = """
⠀⠀⠀⠀⣀⣤⣶⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣶⣤⣀⠀⠀⠀⠀
⠀⠀⣠⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣄⠀⠀
⠀⢰⣿⣿⣿⣿⣿⣿⣿⡿⠿⠿⠿⠿⢿⣿⣿⣿⣿⣿⣿⣿⣿⡆⠀
⢠⣿⣿⣿⣿⣿⡿⠋⣁⣤⣶⣶⣶⣤⣈⠙⢿⣿⣿⣿⣿⣿⣿⣿⡄
⣿⣿⣿⣿⣿⡟⢀⣾⣿⣿⣿⣿⣿⣿⣿⣷⡀⢻⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⠁⣼⣿⣿⣿⣿⣿⣿⣿⣿⣿⣧⠈⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⡏⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⢹⣿⣿⣿⣿⣿⣿
⢿⣿⣿⣿⣿⠘⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠃⣿⣿⣿⣿⣿⣿⡿
⠈⢿⣿⣿⣿⣧⡙⠻⢿⣿⣿⣿⣿⣿⡿⠟⢋⣼⣿⣿⣿⣿⡿⠁⠀
⠀⠀⠙⢿⣿⣿⣿⣷⣤⣈⣉⣉⣉⣁⣤⣾⣿⣿⣿⣿⡿⠋⠀⠀⠀
⠀⠀⠀⠀⠉⠻⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠟⠉⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠉⠛⠛⠛⠛⠛⠛⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀
        """

        console.print(Panel(
            Align.center(Text(banner_text, style=f"bold {AI_COLOR}")),
            border_style=AI_COLOR,
            padding=(1, 2)
        ))

        print_theme("main")

        # Status panel
        status_table = Table(show_header=False, box=None, padding=(0, 2))
        status_table.add_row("📅 Session ID:", f"[{INFO_COLOR}]{self.session_id}[/]")
        status_table.add_row("📂 Results Dir:", f"[{INFO_COLOR}]{self.results_dir}[/]")
        if self.ollama_available and self.selected_model:
            status_table.add_row("🤖 AI Model:", f"[{SUCCESS_COLOR}]{self.selected_model}[/]")
        else:
            status_table.add_row("🤖 AI Model:", f"[{WARNING_COLOR}]Not Available[/]")

        available_tools = sum(1 for t in self.tools_status.values() if t['available'])
        total_tools = len(self.tools_status)
        status_table.add_row("🛠️ Tools Found:", f"[{SUCCESS_COLOR}]{available_tools}/{total_tools}[/]")
        status_table.add_row("🎯 Targets:", f"[{INFO_COLOR}]{len(self.targets)} loaded[/]")

        console.print(Panel(status_table, title="[bold]🔍 System Status[/]", border_style=INFO_COLOR))

        # Non-blocking legal & ethical usage notice (beginning)
        legal = Panel(
            Align.center(Text(
                "AUTHORIZED TESTING ONLY. Use this framework with explicit permission.\n"
                "This notice is informational and does not block operation.",
                style="yellow"
            )),
            title="⚖️ Legal & Ethics",
            border_style="yellow",
        )
        console.print(legal)

    def show_main_menu(self):
        """Display main menu and handle selection"""
        while True:
            console.clear()
            self.show_banner()

            menu_table = Table(show_header=False, box=box.ROUNDED, border_style=USER_COLOR)
            menu_table.add_column("Option", style=f"bold {USER_COLOR}", width=8)
            menu_table.add_column("Description", style="white")
            menu_table.add_column("Status", justify="center", width=12)

            menu_table.add_row("1", "🔍 OSINT & Reconnaissance", self._get_phase_status(TestPhase.OSINT))
            menu_table.add_row("2", "🌐 Network Enumeration", self._get_phase_status(TestPhase.ENUMERATION))
            menu_table.add_row("3", "🔎 Vulnerability Scanning", self._get_phase_status(TestPhase.VULNERABILITY_SCAN))
            menu_table.add_row("4", "💥 Exploitation", self._get_phase_status(TestPhase.EXPLOITATION))
            menu_table.add_row("5", "🔓 Post-Exploitation", self._get_phase_status(TestPhase.POST_EXPLOITATION))
            menu_table.add_row("6", "📊 Log Analysis", self._get_phase_status(TestPhase.LOG_ANALYSIS))
            menu_table.add_row("7", "🤖 AI Chat Assistant", "[cyan]Available[/]" if self.ollama_available else "[red]Offline[/]")
            menu_table.add_row("8", "🤖 🔥 AUTONOMOUS AI AGENT", "[bold red]Full Auto Mode[/]" if self.ollama_available else "[red]AI Offline[/]")
            menu_table.add_row("9", "🎯 Target Management", f"[green]{len(self.targets)} Targets[/]")
            menu_table.add_row("10", "⚙️ Tool Status", "[green]Check Tools[/]")
            menu_table.add_row("11", "📝 Generate Report", "[yellow]Create Report[/]")
            menu_table.add_row("12", "👤 Individual OSINT Investigation", "[cyan]Private Investigations[/]")
            menu_table.add_row("13", "📡 Wireless Network Pentest", "[magenta]WiFi Security Testing[/]")
            menu_table.add_row("0", "❌ Exit", "[red]Quit[/]")

            console.print(Panel(menu_table, title="[bold magenta]👁️ REDEYESdontcry Main Menu[/]"))

            try:
                choice = Prompt.ask(f"[{USER_COLOR}]Select option[/]", 
                                  choices=['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13'])

                if choice == '0':
                    self._cleanup_and_exit()
                elif choice == '1':
                    self.osint_menu()
                elif choice == '2':
                    self.enumeration_menu()
                elif choice == '3':
                    self.vulnerability_menu()
                elif choice == '4':
                    self.exploitation_menu()
                elif choice == '5':
                    self.post_exploitation_menu()
                elif choice == '6':
                    self.log_analysis_menu()
                elif choice == '7':
                    self.chat_interface()
                elif choice == '8':
                    self.autonomous_agent_interface()
                elif choice == '9':
                    self.target_management()
                elif choice == '10':
                    self.show_tool_status()
                elif choice == '11':
                    self.generate_report()
                elif choice == '12':
                    self.individual_osint_menu()
                elif choice == '13':
                    self.wireless_pentest_menu()

            except KeyboardInterrupt:
                self._cleanup_and_exit()
            except Exception as e:
                console.print(f"[{ERROR_COLOR}]Menu error: {e}[/]")
                time.sleep(2)

    def _get_phase_status(self, phase: TestPhase) -> str:
        """Get status indicator for test phase"""
        if phase == self.current_phase:
            return "[yellow]⏳ Current[/]"
        return "[green]✅ Ready[/]"

    def osint_menu(self):
        """OSINT and reconnaissance menu"""
        self.current_phase = TestPhase.OSINT

        while True:
            console.clear()
            console.print(Panel(
                Text("🔍 OSINT & Reconnaissance", style=f"bold {USER_COLOR}"),
                border_style=USER_COLOR
            ))
            print_theme("osint")

            osint_table = Table(show_header=False, box=box.ROUNDED)
            osint_table.add_column("Option", style=f"bold {USER_COLOR}", width=8)
            osint_table.add_column("Tool/Action", style="white") 
            osint_table.add_column("Status", width=12)

            osint_table.add_row("1", "🌐 Domain/IP Information (whois)", self._tool_status('whois'))
            osint_table.add_row("2", "🔍 DNS Reconnaissance", self._tool_status('dnsrecon'))
            osint_table.add_row("3", "📡 Subdomain Enumeration", self._tool_status('amass'))
            osint_table.add_row("4", "🕷️ The Harvester", self._tool_status('theharvester'))
            osint_table.add_row("5", "🌍 Shodan Search", self._tool_status('shodan'))
            osint_table.add_row("6", "⚔️ Fierce DNS Scanner", self._tool_status('fierce'))
            osint_table.add_row("7", "🔧 Custom OSINT Workflow", "[green]Available[/]")
            osint_table.add_row("8", "🤖 AI-Powered OSINT Analysis", "[green]Available[/]" if self.ollama_available else "[red]Offline[/]")
            osint_table.add_row("0", "⬅️ Back to Main Menu", "")

            console.print(osint_table)

            try:
                choice = Prompt.ask(f"[{USER_COLOR}]Select OSINT option[/]",
                                  choices=['0', '1', '2', '3', '4', '5', '6', '7', '8'])

                if choice == '0':
                    break
                elif choice == '1':
                    self.run_whois_lookup()
                elif choice == '2':
                    self.run_dns_recon()
                elif choice == '3':
                    self.run_subdomain_enum()
                elif choice == '4':
                    self.run_harvester()
                elif choice == '5':
                    self.run_shodan_search()
                elif choice == '6':
                    self.run_fierce()
                elif choice == '7':
                    self.custom_osint_workflow()
                elif choice == '8':
                    self.ai_osint_analysis()

            except KeyboardInterrupt:
                break

    def _tool_status(self, tool_name: str) -> str:
        """Get tool availability status"""
        if tool_name in self.tools_status:
            return "[green]✅ Available[/]" if self.tools_status[tool_name]['available'] else "[red]❌ Missing[/]"
        return "[yellow]🔧 System Tool[/]"

    def run_whois_lookup(self):
        """Run whois lookup"""
        target = Prompt.ask(f"[{USER_COLOR}]Enter domain or IP[/]")

        with console.status(f"[{AI_COLOR}]🔍 Running whois lookup on {target}...[/]"):
            try:
                result = subprocess.run(['whois', target], 
                                      capture_output=True, text=True, timeout=30)

                if result.stdout:
                    # Save results
                    output_file = self.results_dir / f'whois_{target.replace(".", "_").replace(":", "_")}.txt'
                    with open(output_file, 'w') as f:
                        f.write(result.stdout)

                    # Display results (truncated)
                    display_text = result.stdout[:2000] + "\n\n[...truncated...]" if len(result.stdout) > 2000 else result.stdout
                    console.print(Panel(
                        Syntax(display_text, "text", theme="monokai"),
                        title=f"🌐 Whois Results for {target}",
                        border_style=SUCCESS_COLOR
                    ))

                    console.print(f"[{INFO_COLOR}]💾 Full results saved to: {output_file}[/]")

                    # AI analysis if available
                    if self.ollama_available:
                        with console.status(f"[{AI_COLOR}]🤖 AI analyzing whois data...[/]"):
                            analysis = self.query_ollama(
                                f"Analyze this whois information for {target} and identify key reconnaissance points, potential attack vectors, and interesting details: {result.stdout[:1500]}",
                                "You are a professional penetration tester analyzing whois data. Focus on actionable intelligence."
                            )
                        console.print(Panel(
                            Text(analysis, style=AI_COLOR),
                            title="[red]🤖 AI Analysis[/]",
                            border_style=AI_COLOR
                        ))

                else:
                    console.print(f"[{ERROR_COLOR}]❌ No whois results for {target}[/]")

            except Exception as e:
                console.print(f"[{ERROR_COLOR}]❌ Whois lookup failed: {e}[/]")

        input("\n⏸️ Press Enter to continue...")

    def run_dns_recon(self):
        """Run DNS reconnaissance"""
        target = Prompt.ask(f"[{USER_COLOR}]Enter target domain[/]")

        if not self.tools_status.get('dnsrecon', {}).get('available'):
            console.print(f"[{WARNING_COLOR}]⚠️ dnsrecon not available - using dig instead[/]")
            with console.status(f"[{AI_COLOR}]🔍 Running basic DNS lookup...[/]"):
                try:
                    # Try multiple record types
                    record_types = ['A', 'AAAA', 'MX', 'NS', 'TXT', 'SOA', 'CNAME']
                    all_results = []

                    for record_type in record_types:
                        cmd = ['dig', '+short', record_type, target]
                        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                        if result.stdout.strip():
                            all_results.append(f"=== {record_type} Records ===")
                            all_results.append(result.stdout.strip())
                            all_results.append("")

                    if all_results:
                        combined_output = "\n".join(all_results)

                        output_file = self.results_dir / f'dns_{target.replace(".", "_")}.txt'
                        with open(output_file, 'w') as f:
                            f.write(combined_output)

                        console.print(Panel(
                            Syntax(combined_output, "text", theme="monokai", word_wrap=True),
                            title=f"🔍 DNS Information - {target}",
                            border_style=SUCCESS_COLOR
                        ))

                        console.print(f"[{INFO_COLOR}]💾 Results saved to: {output_file}[/]")
                    else:
                        console.print(f"[{WARNING_COLOR}]⚠️ No DNS records found for {target}[/]")

                except Exception as e:
                    console.print(f"[{ERROR_COLOR}]❌ DNS lookup failed: {e}[/]")
        else:
            with console.status(f"[{AI_COLOR}]🔍 Running comprehensive DNS reconnaissance...[/]"):
                try:
                    cmd = ['dnsrecon', '-d', target, '-t', 'std']
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

                    output_file = self.results_dir / f'dnsrecon_{target.replace(".", "_")}.txt'
                    with open(output_file, 'w') as f:
                        f.write(result.stdout)

                    console.print(Panel(
                        Syntax(result.stdout[:3000] + ("\n\n[...truncated...]" if len(result.stdout) > 3000 else ""), 
                               "text", theme="monokai", word_wrap=True),
                        title=f"🔍 DNS Reconnaissance - {target}",
                        border_style=SUCCESS_COLOR
                    ))

                    console.print(f"[{INFO_COLOR}]💾 Full results saved to: {output_file}[/]")

                    # Extract key information for context
                    self.context_data['dns_info'] = result.stdout

                    # AI analysis
                    if self.ollama_available:
                        with console.status(f"[{AI_COLOR}]🤖 AI analyzing DNS data...[/]"):
                            analysis = self.query_ollama(
                                f"Analyze these DNS reconnaissance results for {target} and suggest next steps, interesting findings, and potential attack vectors: {result.stdout[:2000]}",
                                "You are an expert in DNS reconnaissance and network security. Provide actionable next steps."
                            )
                        console.print(Panel(
                            Text(analysis, style=AI_COLOR),
                            title="[red]🤖 AI DNS Analysis[/]",
                            border_style=AI_COLOR
                        ))

                except Exception as e:
                    console.print(f"[{ERROR_COLOR}]❌ DNS reconnaissance failed: {e}[/]")

        input("\n⏸️ Press Enter to continue...")

    def chat_interface(self):
        """AI chat interface with context and optional command execution (with confirmation)."""
        if not self.ollama_available:
            console.print(f"[{ERROR_COLOR}]❌ AI chat not available - Ollama offline[/]")
            console.print(f"[{INFO_COLOR}]💡 Install Ollama and uncensored models to enable AI features[/]")
            input("Press Enter to continue...")
            return

        console.clear()
        console.print(Panel(
            Text(f"🤖 AI Chat Assistant - Model: {self.selected_model}", style=f"bold {AI_COLOR}"),
            border_style=AI_COLOR
        ))
        print_theme("chat")

        # Show current context
        context_info = []
        if self.current_target:
            target = self.targets.get(self.current_target)
            if target:
                context_info.append(f"🎯 Current Target: {target.ip}")
                context_info.append(f"🔌 Open Ports: {len(target.open_ports)}")
                context_info.append(f"🔍 Vulnerabilities: {len(target.vulnerabilities)}")

        context_info.append(f"📊 Total Targets: {len(self.targets)}")
        context_info.append(f"📋 Current Phase: {self.current_phase.value}")

        if context_info:
            console.print(Panel(
                Text("\n".join(context_info), style="cyan"),
                title="📊 Current Context",
                border_style="cyan"
            ))

        # Show recent chat history
        if self.chat_history:
            console.print("\n[dim]💬 Recent chat history:[/]")
            for msg in self.chat_history[-4:]:  # Show last 4 messages
                color = USER_COLOR if msg.sender == 'user' else AI_COLOR
                icon = "🧑" if msg.sender == 'user' else "🤖"
                preview = msg.content[:80] + "..." if len(msg.content) > 80 else msg.content
                console.print(f"[{color}]{icon} {msg.sender.upper()}:[/] {preview}")

        console.print("\n[dim]💡 Type 'exit', 'quit', or 'back' to return to main menu[/]")
        console.print("[dim]💡 Ask about targets, tools, techniques, or get pentesting advice![/]")

        while True:
            try:
                user_input = Prompt.ask(f"[{USER_COLOR}]🧑 You[/]")

                if user_input.lower() in ['exit', 'quit', 'back', 'menu']:
                    break

                # Special commands
                if user_input.lower() == 'help':
                    help_text = """
🤖 AI Chat Commands:
• Ask about current targets and scan results
• Get exploitation suggestions and techniques  
• Request specific tool usage guidance
• Discuss pentesting methodologies
• Get help with command syntax

Example queries:
• "How should I exploit the open ports on my current target?"
• "What nmap scripts should I run next?"
• "Analyze the vulnerabilities I found"
• "Give me a step-by-step attack plan"
                    """
                    console.print(Panel(Text(help_text.strip(), style="cyan"), 
                                      title="🤖 Chat Help", border_style="cyan"))
                    continue

                # Query AI with context
                with console.status(f"[{AI_COLOR}]🤖 AI thinking...[/]"):
                    response = self.query_ollama(
                        user_input,
                        "You are an expert penetration tester and cybersecurity professional. Provide detailed, practical, and actionable advice. Include specific commands and techniques when relevant. Return commands in fenced code blocks where possible."
                    )

                console.print(f"[{AI_COLOR}]🤖 AI:[/] {response}")
                console.print()

                # Try to extract commands from AI response
                commands = self._extract_commands(response)
                if commands:
                    console.print(Panel(Text("\n".join([f"{i+1}. {cmd}" for i, cmd in enumerate(commands)]), style="yellow"), title="Suggested commands", border_style="yellow"))
                    if Confirm.ask(f"[{USER_COLOR}]Execute any of the suggested commands?[/]"):
                        while True:
                            try:
                                idx = Prompt.ask(f"[{USER_COLOR}]Enter command number to run (or 'q' to stop)[/]", default='q')
                                if idx.lower() in ['q', 'quit', 'exit', 'n']:
                                    break
                                if not idx.isdigit() or int(idx) < 1 or int(idx) > len(commands):
                                    console.print(f"[{WARNING_COLOR}]Invalid selection[/]")
                                    continue
                                cmd_to_run = commands[int(idx)-1]
                                if Confirm.ask(f"[{WARNING_COLOR}]Confirm execute[/]: {cmd_to_run}"):
                                    self._execute_and_capture(cmd_to_run)
                            except KeyboardInterrupt:
                                break

            except KeyboardInterrupt:
                break
            except Exception as e:
                console.print(f"[{ERROR_COLOR}]❌ Chat error: {e}[/]")

    def _extract_commands(self, text: str) -> List[str]:
        """Extract plausible shell commands from AI output.
        Looks for fenced code blocks and single-line commands starting with known tool names.
        """
        cmds: List[str] = []
        # Extract fenced code blocks
        code_blocks = re.findall(r"```(?:bash|sh|zsh|shell)?\n([\s\S]*?)```", text, re.IGNORECASE)
        for block in code_blocks:
            for line in block.splitlines():
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                cmds.append(line)
        # Fallback: single lines that start with known tools
        known = list(self.tools_status.keys()) + ['dig', 'ping', 'curl', 'wget']
        for line in text.splitlines():
            s = line.strip()
            if not s or s.startswith('#'):
                continue
            token = s.split()[0]
            if token in known and s not in cmds:
                cmds.append(s)
        # Deduplicate preserving order
        seen = set()
        deduped = []
        for c in cmds:
            if c not in seen:
                deduped.append(c)
                seen.add(c)
        return deduped[:10]

    def _execute_and_capture(self, command: str) -> None:
        """Execute a shell command with confirmation already obtained, capture output, and save to file."""
        console.print(f"[{INFO_COLOR}]Running: {command}[/]")
        try:
            ts = datetime.now().strftime('%Y%m%d_%H%M%S')
            out_dir = self.results_dir / 'commands'
            out_dir.mkdir(exist_ok=True)
            outfile = out_dir / f"cmd_{ts}.txt"
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=900)
            with open(outfile, 'w') as f:
                f.write(f"$ {command}\n\n")
                f.write(result.stdout or '')
                if result.stderr:
                    f.write("\n[stderr]\n" + result.stderr)
            status = "OK" if result.returncode == 0 else f"Exit {result.returncode}"
            console.print(Panel(Text(f"Saved to: {outfile}\nStatus: {status}", style=SUCCESS_COLOR if result.returncode == 0 else WARNING_COLOR), title="Command Result", border_style=SUCCESS_COLOR if result.returncode == 0 else WARNING_COLOR))
        except subprocess.TimeoutExpired:
            console.print(f"[{ERROR_COLOR}]Command timed out[/]")
        except Exception as e:
            console.print(f"[{ERROR_COLOR}]Execution failed: {e}[/]")

    # Completed OSINT implementations
    def run_subdomain_enum(self):
        """Complete subdomain enumeration implementation"""
        from redeyes_implementations import CompletedImplementations
        CompletedImplementations.run_subdomain_enum(self)

    def run_harvester(self):
        """Complete theHarvester implementation"""
        from redeyes_implementations import CompletedImplementations
        CompletedImplementations.run_harvester(self)

    def run_shodan_search(self):
        """Shodan search implementation"""
        from redeyes_implementations import CompletedImplementations
        CompletedImplementations.run_shodan_search(self)

    def run_fierce(self):
        """Fierce DNS scanner implementation"""
        from redeyes_implementations import CompletedImplementations
        CompletedImplementations.run_fierce(self)

    def custom_osint_workflow(self):
        """Custom OSINT workflow with multiple tools"""
        from redeyes_implementations import CompletedImplementations
        CompletedImplementations.custom_osint_workflow(self)

    def ai_osint_analysis(self):
        if not self.ollama_available:
            console.print(f"[{ERROR_COLOR}]❌ AI not available[/]")
            input("Press Enter to continue...")
            return

        target = Prompt.ask(f"[{USER_COLOR}]Enter target for AI OSINT analysis[/]")

        with console.status(f"[{AI_COLOR}]🤖 AI analyzing OSINT strategy for {target}...[/]"):
            analysis = self.query_ollama(
                f"Provide a comprehensive OSINT strategy for target: {target}. Include specific tools, techniques, search queries, and step-by-step methodology.",
                "You are an expert OSINT investigator and penetration tester. Provide detailed, actionable reconnaissance strategies."
            )

        console.print(Panel(
            Text(analysis, style=AI_COLOR),
            title=f"[red]🤖 AI OSINT Strategy for {target}[/]",
            border_style=AI_COLOR
        ))
        input("\n⏸️ Press Enter to continue...")

    def enumeration_menu(self):
        """Complete network enumeration menu"""
        from redeyes_implementations import CompletedImplementations
        print_theme("enum")
        CompletedImplementations.enumeration_menu(self)

    def vulnerability_menu(self):
        """Vulnerability scanning menu with complete implementation"""
        from redeyes_implementations import CompletedImplementations
        print_theme("vuln")
        CompletedImplementations.vulnerability_menu(self)

    def exploitation_menu(self):
        """Exploitation menu with complete implementation"""
        from redeyes_implementations import CompletedImplementations
        print_theme("exploit")
        CompletedImplementations.exploitation_menu(self)

    def post_exploitation_menu(self):
        """Post-exploitation menu with complete implementation"""
        from redeyes_implementations import CompletedImplementations
        print_theme("post")
        CompletedImplementations.post_exploitation_menu(self)

    def log_analysis_menu(self):
        """Log analysis menu placeholder"""
        print_theme("report")
        console.print(f"[{INFO_COLOR}]📊 Log Analysis Menu - Full implementation in progress![/]")
        input("Press Enter to continue...")

    def show_tool_status(self):
        """Show comprehensive tool and environment status."""
        console.clear()
        print_theme("tools")
        from rich.table import Table
        table = Table(title="Detected Tools", show_lines=False)
        table.add_column("Tool", style="cyan")
        table.add_column("Status", style="yellow")
        table.add_column("Path", style="green")
        available_tools = 0
        for name, info in sorted(self.tools_status.items()):
            if info.get('available'):
                available_tools += 1
                status = "[green]✅ Available[/]"
                path = info.get('path') or ""
            else:
                status = "[red]❌ Missing[/]"
                path = ""
            table.add_row(name, status, path)
        console.print(table)
        console.print(f"\n[cyan]Ollama:[/] {'[green]Online[/]' if self.ollama_available else '[red]Offline[/]'}  "
                      f"Model: {self.selected_model or 'N/A'}")
        console.print(f"[cyan]Results Dir:[/] {self.results_dir}")
        console.print(f"[cyan]Tools Found:[/] [green]{available_tools}/{len(self.tools_status)}[/]")
        import os as _os
        if _os.getenv("REDEYES_CHECK_MODE") != "1":
            input("\n⏸️ Press Enter to continue...")
    
    def autonomous_agent_interface(self):
        """Autonomous AI Agent interface for full red team automation"""
        if not self.ollama_available:
            console.print(f"[{ERROR_COLOR}]❌ AI not available - Ollama offline[/]")
            console.print(f"[{INFO_COLOR}]💡 Install Ollama and models to enable autonomous operations[/]")
            input("Press Enter to continue...")
            return
        
        console.clear()
        console.print(Panel(
            Text("🤖 🔥 AUTONOMOUS AI AGENT", style=f"bold {AI_COLOR}"),
            subtitle="Full automation from OSINT to exploitation and reporting",
            border_style=AI_COLOR
        ))
        print_theme("agent")
        
        # Model selection interface
        current_model = self.select_ai_model()
        if not current_model:
            return
        
        console.print(f"\n[{SUCCESS_COLOR}]🤖 Selected Model: {current_model}[/]")
        
        # Import and initialize AI Agent
        try:
            from ai_agent import AIAgent
            agent = AIAgent(self)
        except ImportError as e:
            console.print(f"[{ERROR_COLOR}]❌ Could not import AI Agent: {e}[/]")
            input("Press Enter to continue...")
            return
        
        # Autonomous operation menu
        while True:
            console.print("\n")
            agent_table = Table(show_header=False, box=box.ROUNDED, border_style=AI_COLOR)
            agent_table.add_column("Option", style=f"bold {AI_COLOR}", width=8)
            agent_table.add_column("Operation", style="white")
            agent_table.add_column("Status", width=12)
            
            agent_table.add_row("1", "🚀 Full Autonomous Red Team Operation", "[bold red]DANGER[/]")
            agent_table.add_row("2", "🔍 Autonomous OSINT Only", "[yellow]Safe Mode[/]")
            agent_table.add_row("3", "🌐 Autonomous Network Enumeration", "[yellow]Safe Mode[/]")
            agent_table.add_row("4", "🔎 Autonomous Vulnerability Assessment", "[orange3]Moderate[/]")
            agent_table.add_row("5", "💥 Autonomous Exploitation (CAREFUL!)", "[bold red]HIGH RISK[/]")
            agent_table.add_row("6", "🔧 Configure AI Agent Settings", "[green]Configure[/]")
            agent_table.add_row("7", "📊 View Previous Operations Log", "[cyan]History[/]")
            agent_table.add_row("0", "⬅️ Back to Main Menu", "")
            
            console.print(Panel(agent_table, title="[bold red]🤖 Autonomous AI Agent Control Panel[/]", border_style=AI_COLOR))
            
            try:
                choice = Prompt.ask(f"[{AI_COLOR}]Select autonomous operation[/]",
                                  choices=['0','1','2','3','4','5','6','7'])
                
                if choice == '0':
                    break
                elif choice == '1':
                    self._run_full_autonomous_redteam(agent)
                elif choice == '2':
                    self._run_autonomous_osint(agent)
                elif choice == '3':
                    self._run_autonomous_enumeration(agent)
                elif choice == '4':
                    self._run_autonomous_vulnerability(agent)
                elif choice == '5':
                    self._run_autonomous_exploitation(agent)
                elif choice == '6':
                    self._configure_ai_agent(agent)
                elif choice == '7':
                    self._show_operations_log(agent)
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                console.print(f"[{ERROR_COLOR}]❌ Agent error: {e}[/]")
                time.sleep(2)
    
    def select_ai_model(self):
        """Enhanced AI model selection interface"""
        if not self.ollama_available or not self.ollama_models:
            console.print(f"[{ERROR_COLOR}]❌ No Ollama models available[/]")
            return None
        
        console.print(Panel(
            Text("🤖 AI Model Selection", style=f"bold {INFO_COLOR}"),
            subtitle="Choose the AI model for autonomous operations",
            border_style=INFO_COLOR
        ))
        
        # Display available models with ratings
        model_table = Table(title="Available AI Models")
        model_table.add_column("#", style="cyan", width=4)
        model_table.add_column("Model Name", style="green")
        model_table.add_column("Type", style="yellow", width=15)
        model_table.add_column("Penetration Testing Rating", style="red", width=25)
        model_table.add_column("Memory Usage", style="blue", width=12)
        
        # Model ratings and classifications
        model_ratings = {
            'neuraldaredevil': ('Specialized Pentest', '⭐⭐⭐⭐⭐ BEST', '4.7GB'),
            'daredevil': ('Specialized Pentest', '⭐⭐⭐⭐⭐ BEST', '4.7GB'),
            'wizard-vicuna': ('Uncensored General', '⭐⭐⭐⭐ EXCELLENT', '3.8GB'),
            'dolphin': ('Uncensored General', '⭐⭐⭐⭐ EXCELLENT', '3.8GB'),
            'codellama': ('Code Specialist', '⭐⭐⭐ GOOD', '3.8GB'),
            'qwen': ('Code/General', '⭐⭐⭐ GOOD', '4.5GB'),
            'deepseek': ('Code Specialist', '⭐⭐⭐ GOOD', '6.0GB'),
            'llama': ('General Purpose', '⭐⭐ MODERATE', '3.8GB'),
            'mistral': ('General Purpose', '⭐⭐ MODERATE', '4.1GB'),
            'gemma': ('General Purpose', '⭐⭐ MODERATE', '2.8GB')
        }
        
        model_choices = []
        for i, model in enumerate(self.ollama_models, 1):
            model_choices.append(str(i))
            
            # Determine model type and rating
            model_type = 'Unknown'
            rating = '⭐ BASIC'
            memory = 'Unknown'
            
            model_lower = model.lower()
            for key, (mtype, mrating, mmem) in model_ratings.items():
                if key in model_lower:
                    model_type = mtype
                    rating = mrating
                    memory = mmem
                    break
            
            # Highlight current model
            name_style = "bold green" if model == self.selected_model else "white"
            model_table.add_row(
                str(i), 
                f"[{name_style}]{model}[/]",
                model_type,
                rating,
                memory
            )
        
        model_choices.append('0')  # Add option to keep current
        model_table.add_row("0", f"[cyan]Keep Current: {self.selected_model}[/]", "-", "-", "-")
        
        console.print(model_table)
        
        # Model selection
        choice = Prompt.ask(
            f"[{USER_COLOR}]Select AI model (0 to keep current)[/]",
            choices=model_choices,
            default='0'
        )
        
        if choice == '0':
            return self.selected_model
        
        selected_model = self.ollama_models[int(choice) - 1]
        
        # Test the model
        console.print(f"\n[{INFO_COLOR}]🔍 Testing model: {selected_model}[/]")
        
        try:
            with console.status(f"[{AI_COLOR}]Testing {selected_model}...[/]"):
                test_response = self.query_ollama(
                    "Say 'Model test successful' if you can respond.",
                    "You are a penetration testing AI assistant."
                )
            
            if "successful" in test_response.lower() or len(test_response) > 10:
                self.selected_model = selected_model
                console.print(f"[{SUCCESS_COLOR}]✅ Model {selected_model} is working![/]")
                
                # Save model preference
                self.logger.info(f"AI model changed to: {selected_model}")
                
                return selected_model
            else:
                console.print(f"[{ERROR_COLOR}]❌ Model test failed, keeping current model[/]")
                return self.selected_model
                
        except Exception as e:
            console.print(f"[{ERROR_COLOR}]❌ Model test error: {e}[/]")
            console.print(f"[{WARNING_COLOR}]Keeping current model: {self.selected_model}[/]")
            return self.selected_model
    
    def _run_full_autonomous_redteam(self, agent):
        """Run complete autonomous red team operation"""
        console.print(Panel(
            "[bold red]⚠️ FULL AUTONOMOUS RED TEAM OPERATION ⚠️[/]\n\n" +
            "This will perform COMPLETE autonomous penetration testing including:\n" +
            "• OSINT reconnaissance\n" +
            "• Network enumeration and port scanning\n" +
            "• Vulnerability assessment\n" +
            "• 💥 ACTIVE EXPLOITATION ATTEMPTS\n" +
            "• Post-exploitation activities\n" +
            "• Comprehensive reporting\n\n" +
            "[bold yellow]ONLY USE ON AUTHORIZED TARGETS![/]",
            title="[bold red]⚠️ DANGER ZONE ⚠️[/]",
            border_style="red"
        ))
        
        if not Confirm.ask(f"[{AI_COLOR}]Do you have WRITTEN AUTHORIZATION for this target?[/]"):
            console.print(f"[{WARNING_COLOR}]Operation cancelled - authorization required[/]")
            return
        
        target = Prompt.ask(f"[{USER_COLOR}]Enter target domain/IP for FULL AUTONOMOUS ATTACK[/]")
        
        if not Confirm.ask(f"[{AI_COLOR}]FINAL WARNING: Launch autonomous attack on {target}?[/]"):
            console.print(f"[{WARNING_COLOR}]Operation cancelled by user[/]")
            return
        
        console.print(f"[{AI_COLOR}]🚀 Launching full autonomous red team operation against {target}...[/]")
        
        try:
            import asyncio
            asyncio.run(agent.execute_autonomous_redteam(target))
        except Exception as e:
            console.print(f"[{ERROR_COLOR}]❌ Autonomous operation failed: {e}[/]")
        
        input("\nPress Enter to continue...")
    
    def _run_autonomous_osint(self, agent):
        """Run autonomous OSINT only"""
        target = Prompt.ask(f"[{USER_COLOR}]Enter target for autonomous OSINT[/]")
        
        console.print(f"[{SUCCESS_COLOR}]🔍 Starting autonomous OSINT reconnaissance on {target}...[/]")
        
        try:
            import asyncio
            asyncio.run(agent._autonomous_osint_phase(target))
        except Exception as e:
            console.print(f"[{ERROR_COLOR}]❌ OSINT operation failed: {e}[/]")
        
        input("\nPress Enter to continue...")
    
    def _run_autonomous_enumeration(self, agent):
        """Run autonomous network enumeration"""
        if not self.targets:
            console.print(f"[{WARNING_COLOR}]No targets loaded. Run OSINT first or add targets manually.[/]")
            return
        
        console.print(f"[{SUCCESS_COLOR}]🌐 Starting autonomous network enumeration...[/]")
        
        try:
            import asyncio
            asyncio.run(agent._autonomous_enumeration_phase())
        except Exception as e:
            console.print(f"[{ERROR_COLOR}]❌ Enumeration failed: {e}[/]")
        
        input("\nPress Enter to continue...")
    
    def _run_autonomous_vulnerability(self, agent):
        """Run autonomous vulnerability assessment"""
        if not self.targets:
            console.print(f"[{WARNING_COLOR}]No targets loaded. Run enumeration first.[/]")
            return
        
        console.print(f"[{SUCCESS_COLOR}]🔎 Starting autonomous vulnerability assessment...[/]")
        
        try:
            import asyncio
            asyncio.run(agent._autonomous_vulnerability_phase())
        except Exception as e:
            console.print(f"[{ERROR_COLOR}]❌ Vulnerability assessment failed: {e}[/]")
        
        input("\nPress Enter to continue...")
    
    def _run_autonomous_exploitation(self, agent):
        """Run autonomous exploitation (high risk)"""
        console.print(Panel(
            "[bold red]⚠️ AUTONOMOUS EXPLOITATION MODE ⚠️[/]\n\n" +
            "This will attempt to ACTIVELY EXPLOIT vulnerabilities!\n" +
            "Only use on systems you own or have explicit permission to test.\n\n" +
            "[yellow]This could potentially cause system damage or instability.[/]",
            title="[bold red]⚠️ HIGH RISK OPERATION ⚠️[/]",
            border_style="red"
        ))
        
        if not Confirm.ask(f"[{AI_COLOR}]Do you have WRITTEN AUTHORIZATION for exploitation?[/]"):
            console.print(f"[{WARNING_COLOR}]Exploitation cancelled - authorization required[/]")
            return
        
        if not self.targets:
            console.print(f"[{WARNING_COLOR}]No targets with vulnerabilities found.[/]")
            return
        
        console.print(f"[{AI_COLOR}]💥 Starting autonomous exploitation phase...[/]")
        
        try:
            import asyncio
            asyncio.run(agent._autonomous_exploitation_phase())
        except Exception as e:
            console.print(f"[{ERROR_COLOR}]❌ Exploitation failed: {e}[/]")
        
        input("\nPress Enter to continue...")
    
    def _configure_ai_agent(self, agent):
        """Configure AI agent settings"""
        console.print(Panel(
            Text("🔧 AI Agent Configuration", style=f"bold {INFO_COLOR}"),
            border_style=INFO_COLOR
        ))
        
        config_table = Table(title="Current AI Agent Settings")
        config_table.add_column("Setting", style="cyan")
        config_table.add_column("Value", style="green")
        
        config_table.add_row("AI Model", self.selected_model or "None")
        config_table.add_row("Autonomous Mode", "Enabled" if agent.autonomous_mode else "Disabled")
        config_table.add_row("Max Workers", str(agent.executor._max_workers))
        config_table.add_row("Operations Logged", str(len(agent.operations_log)))
        
        console.print(config_table)
        
        # Configuration options
        console.print("\n[cyan]Configuration Options:[/]")
        console.print("1. Change AI Model")
        console.print("2. Toggle Autonomous Mode")
        console.print("3. Clear Operations Log")
        console.print("4. Export Agent Configuration")
        
        choice = Prompt.ask("[cyan]Select configuration option[/]", choices=['1','2','3','4'], default='1')
        
        if choice == '1':
            self.select_ai_model()
        elif choice == '2':
            if agent.autonomous_mode:
                agent.autonomous_mode = False
                console.print(f"[{WARNING_COLOR}]Autonomous mode disabled[/]")
            else:
                agent.enable_autonomous_mode()
        elif choice == '3':
            if Confirm.ask("Clear all operations log?"):
                agent.operations_log.clear()
                console.print(f"[{SUCCESS_COLOR}]Operations log cleared[/]")
        elif choice == '4':
            config_file = self.results_dir / f'ai_agent_config_{self.session_id}.json'
            config_data = {
                'ai_model': self.selected_model,
                'autonomous_mode': agent.autonomous_mode,
                'session_id': self.session_id,
                'operations_count': len(agent.operations_log)
            }
            
            with open(config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            console.print(f"[{SUCCESS_COLOR}]Configuration exported to: {config_file}[/]")
        
        input("\nPress Enter to continue...")
    
    def _show_operations_log(self, agent):
        """Show AI agent operations history"""
        if not agent.operations_log:
            console.print(f"[{WARNING_COLOR}]No operations logged yet[/]")
            input("Press Enter to continue...")
            return
        
        console.print(Panel(
            Text(f"📊 Operations Log ({len(agent.operations_log)} entries)", style=f"bold {INFO_COLOR}"),
            border_style=INFO_COLOR
        ))
        
        # Create operations summary table
        ops_table = Table(title="Recent AI Operations")
        ops_table.add_column("Time", style="cyan", width=12)
        ops_table.add_column("Phase", style="yellow", width=15)
        ops_table.add_column("Operation", style="white")
        ops_table.add_column("Target", style="green", width=15)
        ops_table.add_column("Status", style="red", width=10)
        
        # Show last 20 operations
        recent_ops = agent.operations_log[-20:] if len(agent.operations_log) > 20 else agent.operations_log
        
        for op in recent_ops:
            timestamp = datetime.fromtimestamp(op['timestamp']).strftime('%H:%M:%S')
            phase = op.get('phase', 'Unknown')[:14]
            command = op.get('command', op.get('ai_plan', 'Analysis'))[:40] + "..."
            target = op.get('target', '-')[:14] if op.get('target') else '-'
            status = "✅ Success" if op.get('success') else "❌ Failed" if 'success' in op else "📊 Analysis"
            
            ops_table.add_row(timestamp, phase, command, target, status)
        
        console.print(ops_table)
        
        # Show summary statistics
        summary = agent.get_operations_summary()
        
        summary_table = Table(title="Operations Summary")
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", style="green")
        
        summary_table.add_row("Total Operations", str(summary['total_operations']))
        summary_table.add_row("Successful Operations", str(summary['successful_operations']))
        summary_table.add_row("Success Rate", f"{summary['successful_operations']/summary['total_operations']*100:.1f}%" if summary['total_operations'] > 0 else "N/A")
        summary_table.add_row("Targets Identified", str(summary['targets_identified']))
        summary_table.add_row("Targets Compromised", str(summary['targets_compromised']))
        summary_table.add_row("Vulnerabilities Found", str(summary['total_vulnerabilities']))
        summary_table.add_row("Phases Completed", ", ".join(summary['phases_completed']))
        
        console.print(summary_table)
        
        input("\nPress Enter to continue...")

    def target_management(self):
        """Target management interface"""
        while True:
            console.clear()
            console.print(Panel(
                Text("🎯 Target Management", style=f"bold {USER_COLOR}"),
                border_style=USER_COLOR
            ))
            
            if self.targets:
                target_table = Table(title="Current Targets")
                target_table.add_column("IP", style="green")
                target_table.add_column("Hostname", style="cyan")
                target_table.add_column("Ports", justify="center")
                target_table.add_column("Services", justify="center")
                target_table.add_column("Status")
                
                for ip, target in self.targets.items():
                    status = "🎯 Current" if ip == self.current_target else ""
                    target_table.add_row(
                        ip,
                        target.hostname or "Unknown",
                        str(len(target.open_ports)),
                        str(len(target.services)),
                        status
                    )
                
                console.print(target_table)
            else:
                console.print(f"[{WARNING_COLOR}]No targets loaded[/]")
            
            # Menu options
            mgmt_table = Table(show_header=False, box=box.ROUNDED)
            mgmt_table.add_column("Option", style=f"bold {USER_COLOR}")
            mgmt_table.add_column("Action", style="white")
            
            mgmt_table.add_row("1", "➕ Add Target Manually")
            mgmt_table.add_row("2", "🎯 Select Current Target")
            mgmt_table.add_row("3", "❌ Remove Target")
            mgmt_table.add_row("4", "💾 Export Target List")
            mgmt_table.add_row("5", "📂 Import Target List")
            mgmt_table.add_row("0", "⬅️ Back to Main Menu")
            
            console.print(mgmt_table)
            
            try:
                choice = Prompt.ask(f"[{USER_COLOR}]Select option[/]",
                                  choices=['0','1','2','3','4','5'])
                
                if choice == '0':
                    break
                elif choice == '1':
                    self._add_target_manually()
                elif choice == '2':
                    self._select_current_target()
                elif choice == '3':
                    self._remove_target()
                elif choice == '4':
                    self._export_targets()
                elif choice == '5':
                    self._import_targets()
            except KeyboardInterrupt:
                break
    
    def _add_target_manually(self):
        """Add target manually"""
        target_input = Prompt.ask(f"[{USER_COLOR}]Enter IP or hostname[/]")
        
        try:
            # Try to resolve if hostname
            if not re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', target_input):
                ip = socket.gethostbyname(target_input)
                hostname = target_input
            else:
                ip = target_input
                try:
                    hostname = socket.gethostbyaddr(ip)[0]
                except:
                    hostname = None
            
            if ip not in self.targets:
                self.targets[ip] = Target(ip=ip, hostname=hostname)
                console.print(f"[{SUCCESS_COLOR}]✅ Added target: {ip} ({hostname or 'No hostname'})[/]")
            else:
                console.print(f"[{WARNING_COLOR}]Target already exists[/]")
        except socket.gaierror:
            console.print(f"[{ERROR_COLOR}]❌ Could not resolve {target_input}[/]")
        except Exception as e:
            console.print(f"[{ERROR_COLOR}]❌ Error: {e}[/]")
        
        input("\nPress Enter to continue...")
    
    def _select_current_target(self):
        """Select current target"""
        if not self.targets:
            console.print(f"[{WARNING_COLOR}]No targets available[/]")
            input("Press Enter to continue...")
            return
        
        target_list = list(self.targets.keys())
        for i, ip in enumerate(target_list, 1):
            current = " (current)" if ip == self.current_target else ""
            console.print(f"  {i}. {ip}{current}")
        
        choice = Prompt.ask(f"[{USER_COLOR}]Select target number[/]",
                          choices=[str(i) for i in range(1, len(target_list)+1)])
        
        self.current_target = target_list[int(choice)-1]
        console.print(f"[{SUCCESS_COLOR}]✅ Selected: {self.current_target}[/]")
        input("Press Enter to continue...")
    
    def _remove_target(self):
        """Remove target"""
        if not self.targets:
            console.print(f"[{WARNING_COLOR}]No targets to remove[/]")
            input("Press Enter to continue...")
            return
        
        target_list = list(self.targets.keys())
        for i, ip in enumerate(target_list, 1):
            console.print(f"  {i}. {ip}")
        
        choice = Prompt.ask(f"[{USER_COLOR}]Select target to remove[/]",
                          choices=[str(i) for i in range(1, len(target_list)+1)])
        
        target_to_remove = target_list[int(choice)-1]
        if Confirm.ask(f"[{WARNING_COLOR}]Remove {target_to_remove}?[/]"):
            del self.targets[target_to_remove]
            if self.current_target == target_to_remove:
                self.current_target = None
            console.print(f"[{SUCCESS_COLOR}]✅ Removed {target_to_remove}[/]")
        
        input("Press Enter to continue...")
    
    def _export_targets(self):
        """Export targets to file"""
        if not self.targets:
            console.print(f"[{WARNING_COLOR}]No targets to export[/]")
            input("Press Enter to continue...")
            return
        
        export_file = self.results_dir / f'targets_{self.session_id}.json'
        
        data = {}
        for ip, target in self.targets.items():
            data[ip] = {
                'hostname': target.hostname,
                'open_ports': target.open_ports,
                'services': target.services,
                'vulnerabilities': target.vulnerabilities[:10] if target.vulnerabilities else []
            }
        
        with open(export_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        console.print(f"[{SUCCESS_COLOR}]✅ Exported {len(self.targets)} targets to: {export_file}[/]")
        input("Press Enter to continue...")
    
    def _import_targets(self):
        """Import targets from file"""
        file_path = Prompt.ask(f"[{USER_COLOR}]Enter path to targets file (JSON)[/]")
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            imported = 0
            for ip, info in data.items():
                if ip not in self.targets:
                    target = Target(
                        ip=ip,
                        hostname=info.get('hostname'),
                        open_ports=info.get('open_ports', []),
                        services=info.get('services', {}),
                        vulnerabilities=info.get('vulnerabilities', [])
                    )
                    self.targets[ip] = target
                    imported += 1
            
            console.print(f"[{SUCCESS_COLOR}]✅ Imported {imported} targets[/]")
        except FileNotFoundError:
            console.print(f"[{ERROR_COLOR}]❌ File not found[/]")
        except json.JSONDecodeError:
            console.print(f"[{ERROR_COLOR}]❌ Invalid JSON file[/]")
        except Exception as e:
            console.print(f"[{ERROR_COLOR}]❌ Import failed: {e}[/]")
        
        input("Press Enter to continue...")

    def show_tool_status(self):
        """Show detailed tool status"""
        console.clear()
        console.print(Panel(
            Text("🛠️ Tool Status Overview", style=f"bold {USER_COLOR}"),
            border_style=USER_COLOR
        ))

        # Display available vs missing tools
        available_count = sum(1 for status in self.tools_status.values() if status['available'])
        total_count = len(self.tools_status)

        console.print(f"\n[{SUCCESS_COLOR}]✅ Available: {available_count}/{total_count} tools[/]")

        # Categorize and show tools
        categories = {
            '🔍 Reconnaissance': ['nmap', 'masscan', 'zmap', 'dnsrecon', 'fierce', 'amass', 'subfinder'],
            '🌐 Web Testing': ['nikto', 'gobuster', 'dirb', 'whatweb', 'wpscan', 'sqlmap'],
            '🌍 OSINT': ['theharvester', 'recon-ng', 'maltego', 'shodan', 'assetfinder', 'httprobe'],
            '🏢 Network Services': ['enum4linux', 'smbclient', 'nbtscan', 'onesixtyone', 'snmpwalk'],
            '💥 Exploitation': ['metasploit', 'hydra', 'john', 'hashcat', 'burpsuite'],
        }

        for category, tools in categories.items():
            if not any(tool in self.tools_status for tool in tools):
                continue

            tool_table = Table(title=f"{category} Tools")
            tool_table.add_column("Tool", style="white", width=15)
            tool_table.add_column("Status", justify="center", width=10)
            tool_table.add_column("Path", style="dim")

            for tool in tools:
                if tool in self.tools_status:
                    status = self.tools_status[tool]
                    status_text = "[green]✅[/]" if status['available'] else "[red]❌[/]"
                    path_text = status['path'] or "Not found"
                    tool_table.add_row(tool, status_text, path_text)

            console.print(tool_table)

        # Installation suggestions
        missing_tools = [tool for tool, status in self.tools_status.items() if not status['available']]
        if missing_tools:
            missing_sample = missing_tools[:10]  # Show first 10
            install_cmd = f"sudo apt install {' '.join(missing_sample)}"
            console.print(Panel(
                Text(f"❌ Missing tools: {', '.join(missing_sample)}\n\n💡 Install with:\n{install_cmd}", style="yellow"),
                title="[yellow]⚙️ Installation Suggestions[/]",
                border_style="yellow"
            ))

        input("\n⏸️ Press Enter to continue...")

    def generate_report(self):
        """Generate comprehensive penetration test report"""
        if not self.targets:
            console.print(f"[{WARNING_COLOR}]No targets to report on[/]")
            input("Press Enter to continue...")
            return
        
        # Report format selection
        report_format = Prompt.ask(
            f"[{USER_COLOR}]Select report format[/]",
            choices=['markdown', 'html', 'text', 'json'],
            default='html'
        )
        
        report_file = self.results_dir / f'report_{self.session_id}.{"html" if report_format == "html" else "md" if report_format == "markdown" else "txt" if report_format == "text" else "json"}'
        
        try:
            # Calculate statistics
            total_targets = len(self.targets)
            total_open_ports = sum(len(t.open_ports) for t in self.targets.values())
            total_vulnerabilities = sum(len(t.vulnerabilities) for t in self.targets.values())
            exploited_targets = sum(1 for t in self.targets.values() if t.exploited)
            
            if report_format == 'html':
                self._generate_html_report(report_file, total_targets, total_open_ports, total_vulnerabilities, exploited_targets)
            elif report_format == 'json':
                self._generate_json_report(report_file)
            else:
                self._generate_markdown_report(report_file, total_targets, total_open_ports, total_vulnerabilities, exploited_targets)
            
            console.print(f"[{SUCCESS_COLOR}]✅ Report generated: {report_file}[/]")
            
            # Show report summary
            summary_table = Table(title="Report Summary")
            summary_table.add_column("Metric", style="cyan")
            summary_table.add_column("Value", style="green")
            
            summary_table.add_row("Total Targets", str(total_targets))
            summary_table.add_row("Open Ports", str(total_open_ports))
            summary_table.add_row("Vulnerabilities Found", str(total_vulnerabilities))
            summary_table.add_row("Exploited Targets", str(exploited_targets))
            summary_table.add_row("Report Format", report_format.upper())
            summary_table.add_row("File Location", str(report_file))
            
            console.print(summary_table)
            
        except Exception as e:
            console.print(f"[{ERROR_COLOR}]❌ Report generation failed: {e}[/]")
        
        input("Press Enter to continue...")
    
    def _generate_html_report(self, report_file, total_targets, total_open_ports, total_vulnerabilities, exploited_targets):
        """Generate HTML report with charts and styling"""
        html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>REDEYESdontcry Penetration Test Report</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background-color: #0a0a0a; color: #fff; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ background: linear-gradient(135deg, #ff0040, #8b0000); padding: 40px; border-radius: 10px; margin-bottom: 30px; text-align: center; }}
        .header h1 {{ color: #fff; font-size: 3em; margin: 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.5); }}
        .header .subtitle {{ color: #ffccd5; font-size: 1.2em; margin-top: 10px; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .stat-card {{ background: #1a1a1a; border: 1px solid #333; border-radius: 8px; padding: 20px; text-align: center; }}
        .stat-number {{ font-size: 2.5em; font-weight: bold; color: #ff0040; margin-bottom: 10px; }}
        .stat-label {{ color: #ccc; font-size: 1.1em; }}
        .section {{ background: #1a1a1a; border: 1px solid #333; border-radius: 8px; margin-bottom: 30px; padding: 30px; }}
        .section h2 {{ color: #ff0040; border-bottom: 2px solid #ff0040; padding-bottom: 10px; margin-bottom: 20px; }}
        .target {{ background: #0d1117; border: 1px solid #30363d; border-radius: 6px; margin-bottom: 20px; padding: 20px; }}
        .target h3 {{ color: #58a6ff; margin-top: 0; }}
        .target-info {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 15px; }}
        .info-item {{ background: #21262d; padding: 10px; border-radius: 4px; }}
        .info-label {{ color: #7d8590; font-size: 0.9em; margin-bottom: 5px; }}
        .info-value {{ color: #f0f6fc; font-weight: 500; }}
        .vuln-list {{ background: #2d1b1b; border-left: 4px solid #ff6b6b; padding: 15px; border-radius: 4px; }}
        .vuln-item {{ color: #ffcccb; margin-bottom: 8px; padding: 5px 0; border-bottom: 1px solid #444; }}
        .vuln-item:last-child {{ border-bottom: none; }}
        .footer {{ text-align: center; padding: 30px; color: #7d8590; font-size: 0.9em; }}
        .critical {{ color: #ff4757; font-weight: bold; }}
        .high {{ color: #ff7675; font-weight: bold; }}
        .medium {{ color: #fdcb6e; font-weight: bold; }}
        .low {{ color: #74b9ff; font-weight: bold; }}
        .services-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 10px; }}
        .service-tag {{ background: #2ea043; color: white; padding: 4px 8px; border-radius: 12px; font-size: 0.8em; text-align: center; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>👁️ REDEYESdontcry</h1>
            <div class="subtitle">Penetration Test Report</div>
            <div class="subtitle">Session: {self.session_id}</div>
            <div class="subtitle">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{total_targets}</div>
                <div class="stat-label">Targets Scanned</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{total_open_ports}</div>
                <div class="stat-label">Open Ports</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{total_vulnerabilities}</div>
                <div class="stat-label">Vulnerabilities</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{exploited_targets}</div>
                <div class="stat-label">Exploited</div>
            </div>
        </div>
        
        <div class="section">
            <h2>🎯 Target Details</h2>
"""
        
        # Add target details
        for ip, target in self.targets.items():
            html_template += f"""
            <div class="target">
                <h3>💻 {ip}</h3>
                <div class="target-info">
                    <div class="info-item">
                        <div class="info-label">Hostname</div>
                        <div class="info-value">{target.hostname or 'Unknown'}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Open Ports</div>
                        <div class="info-value">{len(target.open_ports)} ports</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Services</div>
                        <div class="info-value">{len(target.services)} identified</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Status</div>
                        <div class="info-value {'critical' if target.exploited else 'medium'}">
                            {'☠️ Compromised' if target.exploited else '🔍 Under Assessment'}
                        </div>
                    </div>
                </div>
                
                <div class="info-label">Port Details:</div>
                <div class="services-grid">
"""
            for port in sorted(target.open_ports)[:20]:  # Show first 20 ports
                service = target.services.get(port, 'unknown')
                html_template += f'<div class="service-tag">{port}/{service}</div>'
            
            if len(target.open_ports) > 20:
                html_template += f'<div class="service-tag">... +{len(target.open_ports)-20} more</div>'
                
            html_template += "</div>"
            
            # Add vulnerabilities
            if target.vulnerabilities:
                html_template += """
                <div class="info-label" style="margin-top: 20px;">Vulnerabilities Found:</div>
                <div class="vuln-list">
"""
                for vuln in target.vulnerabilities[:10]:  # Show first 10 vulns
                    severity = 'critical' if any(x in vuln.lower() for x in ['cve', 'exploit', 'critical']) else 'high' if 'vulnerable' in vuln.lower() else 'medium'
                    html_template += f'<div class="vuln-item {severity}">⚠️ {vuln}</div>'
                
                if len(target.vulnerabilities) > 10:
                    html_template += f'<div class="vuln-item">... and {len(target.vulnerabilities)-10} more vulnerabilities</div>'
                    
                html_template += "</div>"
            
            html_template += "</div>"  # Close target div
        
        # Close HTML
        html_template += f"""
        </div>
        
        <div class="section">
            <h2>🤖 AI Analysis Summary</h2>
            <p>{'AI Model: ' + self.selected_model if self.selected_model else 'AI analysis not available'}</p>
            <p>Total AI interactions: {len([msg for msg in self.chat_history if msg.sender == 'user'])}</p>
        </div>
        
        <div class="footer">
            <p>Generated by REDEYESdontcry Framework - Session {self.session_id}</p>
            <p>Report generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
            <p style="color: #ff0040; font-weight: bold;">⚠️ FOR AUTHORIZED TESTING ONLY ⚠️</p>
        </div>
    </div>
</body>
</html>
"""
        
        with open(report_file, 'w') as f:
            f.write(html_template)
    
    def _generate_json_report(self, report_file):
        """Generate JSON report for API/programmatic access"""
        report_data = {
            'session_id': self.session_id,
            'generated_at': datetime.now().isoformat(),
            'ai_model': self.selected_model,
            'summary': {
                'total_targets': len(self.targets),
                'total_open_ports': sum(len(t.open_ports) for t in self.targets.values()),
                'total_vulnerabilities': sum(len(t.vulnerabilities) for t in self.targets.values()),
                'exploited_targets': sum(1 for t in self.targets.values() if t.exploited)
            },
            'targets': {},
            'chat_interactions': len([msg for msg in self.chat_history if msg.sender == 'user'])
        }
        
        for ip, target in self.targets.items():
            report_data['targets'][ip] = {
                'hostname': target.hostname,
                'open_ports': target.open_ports,
                'services': target.services,
                'vulnerabilities': target.vulnerabilities,
                'exploited': target.exploited,
                'shells': target.shells,
                'credentials': target.credentials,
                'notes': target.notes
            }
        
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
    
    def _generate_markdown_report(self, report_file, total_targets, total_open_ports, total_vulnerabilities, exploited_targets):
        """Generate Markdown report"""
        content = [
            f"# 👁️ REDEYESdontcry Penetration Test Report",
            f"",
            f"**Session ID:** {self.session_id}",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**AI Model:** {self.selected_model or 'N/A'}",
            f"",
            f"## 📊 Executive Summary",
            f"",
            f"| Metric | Value |",
            f"|--------|-------|",
            f"| Targets Scanned | {total_targets} |",
            f"| Open Ports | {total_open_ports} |",
            f"| Vulnerabilities | {total_vulnerabilities} |",
            f"| Exploited Targets | {exploited_targets} |",
            f"",
            f"## 🎯 Target Details",
            f""
        ]
        
        for ip, target in self.targets.items():
            status_text = '☠️ Compromised' if target.exploited else '🔍 Under Assessment'
            content.extend([
                f"### 💻 {ip}",
                f"",
                f"- **Hostname:** {target.hostname or 'Unknown'}",
                f"- **Status:** {status_text}",
                f"- **Open Ports ({len(target.open_ports)}):** {', '.join(map(str, sorted(target.open_ports)[:20]))}",
                f"- **Services:** {len(target.services)} identified",
                f""
            ])
            
            if target.vulnerabilities:
                content.extend([
                    f"#### ⚠️ Vulnerabilities ({len(target.vulnerabilities)} found)",
                    f""
                ])
                
                for vuln in target.vulnerabilities[:15]:  # Show first 15
                    content.append(f"- {vuln}")
                
                if len(target.vulnerabilities) > 15:
                    content.append(f"- ... and {len(target.vulnerabilities)-15} more vulnerabilities")
                content.append("")
        
        content.extend([
            f"## 🤖 AI Analysis",
            f"",
            f"- **AI Model Used:** {self.selected_model or 'None'}",
            f"- **Total AI Interactions:** {len([msg for msg in self.chat_history if msg.sender == 'user'])}",
            f"",
            f"## 📋 Session Information",
            f"",
            f"- **Session ID:** {self.session_id}",
            f"- **Results Directory:** {self.results_dir}",
            f"- **Tools Available:** {sum(1 for t in self.tools_status.values() if t['available'])}/{len(self.tools_status)}",
            f"",
            f"---",
            f"",
            f"**⚠️ DISCLAIMER:** This report is for authorized penetration testing purposes only."
        ])
        
        with open(report_file, 'w') as f:
            f.write("\n".join(content))

    def individual_osint_menu(self):
        """Individual OSINT investigation menu"""
        try:
            from individual_osint import run_individual_osint_menu
            # Pass the framework instance so modules can access AI functionality
            run_individual_osint_menu(self.session_id, str(self.results_dir), 
                                    self if self.ollama_available else None)
        except ImportError as e:
            console.print(f"[{ERROR_COLOR}]❌ Individual OSINT module not available: {e}[/]")
            console.print(f"[{INFO_COLOR}]💡 Make sure individual_osint.py is in the same directory[/]")
        except Exception as e:
            self.logger.error(f"Individual OSINT error: {e}")
            console.print(f"[{ERROR_COLOR}]❌ Individual OSINT investigation failed: {e}[/]")
        
        input("\n⏸️ Press Enter to continue...")
    
    def wireless_pentest_menu(self):
        """Wireless network penetration testing menu"""
        try:
            from wireless_pentest import run_wireless_pentest_menu
            # Pass the framework instance so modules can access AI functionality
            run_wireless_pentest_menu(self.session_id, str(self.results_dir), 
                                    self if self.ollama_available else None)
        except ImportError as e:
            console.print(f"[{ERROR_COLOR}]❌ Wireless pentest module not available: {e}[/]")
            console.print(f"[{INFO_COLOR}]💡 Make sure wireless_pentest.py is in the same directory[/]")
            console.print(f"[{INFO_COLOR}]💡 Requires: aircrack-ng, airmon-ng, reaver, hostapd[/]")
        except Exception as e:
            self.logger.error(f"Wireless pentest error: {e}")
            console.print(f"[{ERROR_COLOR}]❌ Wireless penetration testing failed: {e}[/]")
        
        input("\n⏸️ Press Enter to continue...")

    def _cleanup_and_exit(self):
        """Cleanup and exit gracefully"""
        console.clear()
        self.show_banner()

        console.print(Panel(
            Text("📊 Session Summary", style=f"bold {SUCCESS_COLOR}"),
            border_style=SUCCESS_COLOR
        ))

        # Calculate session duration
        try:
            session_start = datetime.strptime(self.session_id, '%Y%m%d_%H%M%S')
            duration = datetime.now() - session_start
        except:
            duration = "Unknown"

        summary_table = Table(show_header=False, box=None)
        summary_table.add_row("⏱️ Session Duration:", str(duration))
        summary_table.add_row("🎯 Targets Scanned:", str(len(self.targets)))
        summary_table.add_row("🤖 AI Queries:", str(len([msg for msg in self.chat_history if msg.sender == 'user'])))
        summary_table.add_row("📂 Results Directory:", str(self.results_dir))
        summary_table.add_row("🛠️ Tools Available:", f"{sum(1 for t in self.tools_status.values() if t['available'])}/{len(self.tools_status)}")

        console.print(summary_table)

        if self.targets and Confirm.ask(f"[{USER_COLOR}]📝 Generate final report before exit?[/]"):
            console.print(f"[{INFO_COLOR}]📝 Report generation - Feature coming soon![/]")

        console.print(f"\n[{SUCCESS_COLOR}]👁️ Thanks for using REDEYESdontcry![/]")
        console.print(f"[dim]💾 Session data saved to: {self.results_dir}[/]")
        console.print(f"[dim]🔍 Log file: {self.results_dir}/redeyesdontcry_{self.session_id}.log[/]")

        # Log session end
        self.logger.info(f"REDEYESdontcry session ended: {self.session_id}")

        # Cleanup
        self.executor.shutdown(wait=True)
        sys.exit(0)

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    console.print(f"\n[{WARNING_COLOR}]⚠️ Interrupted by user[/]")
    console.print(f"[dim]💾 Session data preserved in /tmp/redeyesdontcry_*[/]")
    sys.exit(0)

def main():
    """Main entry point"""
    signal.signal(signal.SIGINT, signal_handler)

    try:
        # ASCII art intro
        intro_art = """
        ╔══════════════════════════════════════════╗
        ║          👁️ REDEYESdontcry 👁️            ║
        ║     Advanced Red Team TUI Framework      ║
        ║        With AI Integration 🤖            ║
        ╚══════════════════════════════════════════╝
        """
        console.print(Text(intro_art, style="bold red"))
        time.sleep(1)

        framework = REDEYESFramework()
        framework.show_main_menu()

    except KeyboardInterrupt:
        console.print(f"\n[{WARNING_COLOR}]⚠️ Interrupted by user[/]")
    except Exception as e:
        console.print(f"[{ERROR_COLOR}]💥 Fatal error: {e}[/]")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
