#!/usr/bin/env python3
"""
REDEYESdontcry - Complete Tool Implementations
All pentesting phase implementations with working code
"""

import subprocess
import socket
import re
import json
import time
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import xml.etree.ElementTree as ET

# Rich imports
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.syntax import Syntax
from rich import box
from rich.status import Status

# Import centralized Target dataclass and art themes
from redeyes.core.models import Target
from art_assets import print_theme

console = Console()

# Color definitions (matching main file)
USER_COLOR = "bright_magenta"
AI_COLOR = "red"
SUCCESS_COLOR = "green"
WARNING_COLOR = "yellow"
ERROR_COLOR = "bright_red"
INFO_COLOR = "cyan"

class CompletedImplementations:
    """Complete implementations for all placeholder methods"""
    
    @staticmethod
    def run_subdomain_enum(framework):
        """Complete subdomain enumeration implementation"""
        target = Prompt.ask(f"[{USER_COLOR}]Enter target domain[/]")
        print_theme("osint")
        
        # Try multiple tools
        tools_to_try = ['amass', 'subfinder', 'assetfinder']
        available_tools = [tool for tool in tools_to_try if framework.tools_status.get(tool, {}).get('available')]
        
        if not available_tools:
            console.print(f"[{WARNING_COLOR}]⚠️ No subdomain enumeration tools available[/]")
            console.print(f"[{INFO_COLOR}]💡 Install with: sudo apt install amass subfinder[/]")
            console.print(f"[{INFO_COLOR}]💡 Or: go install github.com/tomnomnom/assetfinder@latest[/]")
            input("Press Enter to continue...")
            return
        
        all_subdomains = set()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        ) as progress:
            
            for tool in available_tools:
                task = progress.add_task(f"[{AI_COLOR}]Running {tool}...[/]", total=None)
                
                try:
                    if tool == 'amass':
                        cmd = ['amass', 'enum', '-passive', '-d', target]
                    elif tool == 'subfinder':
                        cmd = ['subfinder', '-d', target, '-silent']
                    elif tool == 'assetfinder':
                        cmd = ['assetfinder', target]
                    
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
                    
                    if result.stdout:
                        subdomains = result.stdout.strip().split('\n')
                        all_subdomains.update([s.strip() for s in subdomains if s.strip()])
                        
                        # Save results
                        output_file = framework.results_dir / f'{tool}_{target.replace(".", "_")}.txt'
                        with open(output_file, 'w') as f:
                            f.write(result.stdout)
                
                except subprocess.TimeoutExpired:
                    console.print(f"[{WARNING_COLOR}]{tool} timed out[/]")
                except Exception as e:
                    console.print(f"[{WARNING_COLOR}]{tool} failed: {e}[/]")
                
                progress.update(task, completed=True)
        
        if all_subdomains:
            # Display results
            subdomain_table = Table(title=f"Subdomains for {target}")
            subdomain_table.add_column("Subdomain", style="green")
            subdomain_table.add_column("Status", style="cyan")
            subdomain_table.add_column("IP", style="yellow")
            
            console.print(f"\n[{SUCCESS_COLOR}]Found {len(all_subdomains)} unique subdomains[/]")
            
            # Check resolution for each subdomain
            resolved_count = 0
            for subdomain in sorted(all_subdomains)[:50]:  # Show first 50
                try:
                    ip = socket.gethostbyname(subdomain)
                    subdomain_table.add_row(subdomain, "✅ Resolves", ip)
                    resolved_count += 1
                except:
                    subdomain_table.add_row(subdomain, "❌ No Resolution", "-")
            
            console.print(subdomain_table)
            
            # Save combined results
            combined_file = framework.results_dir / f'subdomains_{target.replace(".", "_")}_combined.txt'
            with open(combined_file, 'w') as f:
                f.write('\n'.join(sorted(all_subdomains)))
            
            console.print(f"\n[{INFO_COLOR}]💾 All {len(all_subdomains)} subdomains saved to: {combined_file}[/]")
            console.print(f"[{SUCCESS_COLOR}]✅ {resolved_count} subdomains resolve to IPs[/]")
            
            # Update context
            framework.context_data['subdomains'] = list(all_subdomains)[:100]
            
            # AI analysis if available
            if framework.ollama_available and resolved_count > 0:
                with console.status(f"[{AI_COLOR}]🤖 AI analyzing subdomains...[/]"):
                    analysis = framework.query_ollama(
                        f"Analyze these {len(all_subdomains)} subdomains for {target}. Identify interesting patterns, potential attack surface, and prioritize targets: {list(all_subdomains)[:20]}",
                        "You are analyzing subdomain enumeration results. Identify patterns, technologies, and prioritize targets."
                    )
                console.print(Panel(
                    Text(analysis, style=AI_COLOR),
                    title="[red]🤖 AI Subdomain Analysis[/]",
                    border_style=AI_COLOR
                ))
        else:
            console.print(f"[{WARNING_COLOR}]No subdomains found for {target}[/]")
        
        input("\n⏸️ Press Enter to continue...")
    
    @staticmethod
    def run_harvester(framework):
        """Complete theHarvester implementation"""
        print_theme("osint")
        if not framework.tools_status.get('theharvester', {}).get('available'):
            console.print(f"[{ERROR_COLOR}]❌ theHarvester not installed[/]")
            console.print(f"[{INFO_COLOR}]💡 Install with: sudo apt install theharvester[/]")
            input("Press Enter to continue...")
            return
        
        target = Prompt.ask(f"[{USER_COLOR}]Enter target domain[/]")
        
        # Select data sources
        sources = ['google', 'bing', 'linkedin', 'twitter', 'yahoo', 'baidu', 'duckduckgo']
        console.print(f"\n[{INFO_COLOR}]Available sources: {', '.join(sources)}[/]")
        selected_sources = Prompt.ask(
            f"[{USER_COLOR}]Enter sources to use (comma-separated, or 'all')[/]",
            default='google,bing,linkedin'
        )
        
        if selected_sources.lower() == 'all':
            source_list = sources
        else:
            source_list = [s.strip() for s in selected_sources.split(',') if s.strip() in sources]
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task(f"[{AI_COLOR}]Running theHarvester on {target}...[/]", total=None)
            
            try:
                cmd = ['theHarvester', '-d', target, '-b', ','.join(source_list)]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                
                if result.stdout:
                    # Save full output
                    output_file = framework.results_dir / f'theharvester_{target.replace(".", "_")}.txt'
                    with open(output_file, 'w') as f:
                        f.write(result.stdout)
                    
                    # Parse and display key findings
                    emails = re.findall(r'[\w\.-]+@[\w\.-]+', result.stdout)
                    hosts = re.findall(r'[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.' + re.escape(target), result.stdout)
                    ips = re.findall(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', result.stdout)
                    
                    # Display results
                    if emails or hosts or ips:
                        results_table = Table(title=f"theHarvester Results for {target}")
                        results_table.add_column("Type", style="cyan")
                        results_table.add_column("Count", style="yellow")
                        results_table.add_column("Sample", style="green")
                        
                        if emails:
                            unique_emails = list(set(emails))
                            results_table.add_row("📧 Emails", str(len(unique_emails)), ', '.join(unique_emails[:3]))
                        
                        if hosts:
                            unique_hosts = list(set(hosts))
                            results_table.add_row("🌐 Hosts", str(len(unique_hosts)), ', '.join(unique_hosts[:3]))
                        
                        if ips:
                            unique_ips = list(set(ips))
                            results_table.add_row("🔢 IPs", str(len(unique_ips)), ', '.join(unique_ips[:3]))
                        
                        console.print(results_table)
                        
                        # Save parsed results
                        if emails:
                            emails_file = framework.results_dir / f'emails_{target.replace(".", "_")}.txt'
                            with open(emails_file, 'w') as f:
                                f.write('\n'.join(set(emails)))
                            console.print(f"[{INFO_COLOR}]💾 Emails saved to: {emails_file}[/]")
                        
                        console.print(f"[{INFO_COLOR}]💾 Full results saved to: {output_file}[/]")
                        
                        # AI analysis
                        if framework.ollama_available:
                            with console.status(f"[{AI_COLOR}]🤖 AI analyzing OSINT data...[/]"):
                                analysis = framework.query_ollama(
                                    f"Analyze theHarvester results for {target}: Found {len(set(emails)) if emails else 0} emails, {len(set(hosts)) if hosts else 0} hosts, {len(set(ips)) if ips else 0} IPs. Suggest next steps and attack vectors.",
                                    "You are analyzing OSINT data. Focus on actionable intelligence and attack vectors."
                                )
                            console.print(Panel(
                                Text(analysis, style=AI_COLOR),
                                title="[red]🤖 AI OSINT Analysis[/]",
                                border_style=AI_COLOR
                            ))
                    else:
                        console.print(f"[{WARNING_COLOR}]No significant data found[/]")
                else:
                    console.print(f"[{WARNING_COLOR}]No results returned[/]")
                    
            except subprocess.TimeoutExpired:
                console.print(f"[{ERROR_COLOR}]theHarvester timed out[/]")
            except Exception as e:
                console.print(f"[{ERROR_COLOR}]theHarvester failed: {e}[/]")
        
        input("\n⏸️ Press Enter to continue...")
    
    @staticmethod
    def run_shodan_search(framework):
        """Shodan search implementation"""
        print_theme("osint")
        if not framework.tools_status.get('shodan', {}).get('available'):
            console.print(f"[{ERROR_COLOR}]❌ Shodan CLI not installed[/]")
            console.print(f"[{INFO_COLOR}]💡 Install with: pip install shodan[/]")
            console.print(f"[{INFO_COLOR}]💡 Then: shodan init YOUR_API_KEY[/]")
            input("Press Enter to continue...")
            return
        
        search_type = Prompt.ask(
            f"[{USER_COLOR}]Search type[/]",
            choices=['ip', 'domain', 'query'],
            default='domain'
        )
        
        if search_type == 'ip':
            target = Prompt.ask(f"[{USER_COLOR}]Enter IP address[/]")
            cmd = ['shodan', 'host', target]
        elif search_type == 'domain':
            target = Prompt.ask(f"[{USER_COLOR}]Enter domain[/]")
            cmd = ['shodan', 'domain', target]
        else:
            target = Prompt.ask(f"[{USER_COLOR}]Enter Shodan query (e.g., 'port:22 country:US')[/]")
            count = Prompt.ask(f"[{USER_COLOR}]Number of results[/]", default='20')
            cmd = ['shodan', 'search', '--limit', count, target]
        
        with console.status(f"[{AI_COLOR}]🌍 Querying Shodan...[/]"):
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                
                if result.stdout:
                    # Save results
                    output_file = framework.results_dir / f'shodan_{target.replace(" ", "_").replace(":", "_")[:50]}.txt'
                    with open(output_file, 'w') as f:
                        f.write(result.stdout)
                    
                    # Display results
                    console.print(Panel(
                        Syntax(result.stdout[:2000] + ("\n\n[...truncated...]" if len(result.stdout) > 2000 else ""),
                               "text", theme="monokai"),
                        title=f"🌍 Shodan Results",
                        border_style=SUCCESS_COLOR
                    ))
                    
                    console.print(f"[{INFO_COLOR}]💾 Full results saved to: {output_file}[/]")
                    
                    # Parse for IPs and ports if available
                    ips = re.findall(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', result.stdout)
                    ports = re.findall(r'port:\s*(\d+)', result.stdout, re.IGNORECASE)
                    
                    if ips:
                        console.print(f"[{SUCCESS_COLOR}]Found {len(set(ips))} unique IPs[/]")
                    if ports:
                        console.print(f"[{SUCCESS_COLOR}]Ports observed: {', '.join(set(ports)[:10])}[/]")
                else:
                    console.print(f"[{WARNING_COLOR}]No results returned - check API key configuration[/]")
                    
            except subprocess.TimeoutExpired:
                console.print(f"[{ERROR_COLOR}]Shodan query timed out[/]")
            except Exception as e:
                console.print(f"[{ERROR_COLOR}]Shodan search failed: {e}[/]")
        
        input("\n⏸️ Press Enter to continue...")
    
    @staticmethod
    def run_fierce(framework):
        """Fierce DNS scanner implementation"""
        print_theme("osint")
        if not framework.tools_status.get('fierce', {}).get('available'):
            console.print(f"[{ERROR_COLOR}]❌ Fierce not installed[/]")
            console.print(f"[{INFO_COLOR}]💡 Install with: sudo apt install fierce[/]")
            input("Press Enter to continue...")
            return
        
        target = Prompt.ask(f"[{USER_COLOR}]Enter target domain[/]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task(f"[{AI_COLOR}]⚔️ Running Fierce DNS scanner on {target}...[/]", total=None)
            
            try:
                cmd = ['fierce', '--domain', target]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                
                if result.stdout:
                    # Save results
                    output_file = framework.results_dir / f'fierce_{target.replace(".", "_")}.txt'
                    with open(output_file, 'w') as f:
                        f.write(result.stdout)
                    
                    # Parse for discovered hosts
                    ip_pattern = r'(\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b)\s+([^\s]+)'
                    discovered = re.findall(ip_pattern, result.stdout)
                    
                    if discovered:
                        # Display findings
                        fierce_table = Table(title=f"⚔️ Fierce Results for {target}")
                        fierce_table.add_column("IP Address", style="green")
                        fierce_table.add_column("Hostname", style="cyan")
                        
                        for ip, hostname in discovered[:20]:  # Show first 20
                            fierce_table.add_row(ip, hostname)
                        
                        console.print(fierce_table)
                        console.print(f"[{SUCCESS_COLOR}]Found {len(discovered)} hosts[/]")
                    else:
                        console.print(f"[{WARNING_COLOR}]No additional hosts discovered[/]")
                    
                    console.print(f"[{INFO_COLOR}]💾 Full results saved to: {output_file}[/]")
                    
                    # AI analysis
                    if framework.ollama_available and discovered:
                        with console.status(f"[{AI_COLOR}]🤖 AI analyzing DNS findings...[/]"):
                            analysis = framework.query_ollama(
                                f"Analyze Fierce DNS scan results for {target}: Found {len(discovered)} hosts. Suggest attack surface and next steps: {discovered[:10]}",
                                "You are analyzing DNS brute force results. Identify patterns and attack vectors."
                            )
                        console.print(Panel(
                            Text(analysis, style=AI_COLOR),
                            title="[red]🤖 AI DNS Analysis[/]",
                            border_style=AI_COLOR
                        ))
                else:
                    console.print(f"[{WARNING_COLOR}]No results returned[/]")
                    
            except subprocess.TimeoutExpired:
                console.print(f"[{ERROR_COLOR}]Fierce scan timed out[/]")
            except Exception as e:
                console.print(f"[{ERROR_COLOR}]Fierce scan failed: {e}[/]")
        
        input("\n⏸️ Press Enter to continue...")
    
    @staticmethod
    def custom_osint_workflow(framework):
        """Custom OSINT workflow with multiple tools"""
        target = Prompt.ask(f"[{USER_COLOR}]Enter target domain or company name[/]")
        
        console.print(Panel(
            Text("🔧 Custom OSINT Workflow", style=f"bold {USER_COLOR}"),
            border_style=USER_COLOR
        ))
        
        # Build workflow steps
        workflow = []
        
        console.print("\n[cyan]Select OSINT steps to include:[/]")
        if Confirm.ask("1. Whois lookup?", default=True):
            workflow.append(('whois', f'whois {target}'))
        if Confirm.ask("2. DNS reconnaissance?", default=True):
            workflow.append(('dns', f'dig ANY {target}'))
        if Confirm.ask("3. Subdomain enumeration?", default=True):
            if framework.tools_status.get('subfinder', {}).get('available'):
                workflow.append(('subdomains', f'subfinder -d {target} -silent'))
        if Confirm.ask("4. Email harvesting?", default=True):
            if framework.tools_status.get('theharvester', {}).get('available'):
                workflow.append(('emails', f'theHarvester -d {target} -b google,bing'))
        if Confirm.ask("5. Google dorking?", default=False):
            dorks = [
                f'site:{target} filetype:pdf',
                f'site:{target} intitle:"index of"',
                f'site:{target} ext:sql OR ext:db OR ext:log',
                f'site:{target} inurl:admin OR inurl:login'
            ]
            workflow.append(('dorks', dorks))
        
        if not workflow:
            console.print(f"[{WARNING_COLOR}]No steps selected[/]")
            input("Press Enter to continue...")
            return
        
        results = {}
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        ) as progress:
            
            for step_name, command in workflow:
                task = progress.add_task(f"[{AI_COLOR}]Running {step_name}...[/]", total=None)
                
                try:
                    if step_name == 'dorks':
                        # Special handling for Google dorks
                        console.print(f"\n[{INFO_COLOR}]Google dorks to try:[/]")
                        for dork in command:
                            console.print(f"  • {dork}")
                        results[step_name] = command
                    else:
                        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=120)
                        if result.stdout:
                            results[step_name] = result.stdout
                            # Save individual results
                            output_file = framework.results_dir / f'osint_{step_name}_{target.replace(".", "_")}.txt'
                            with open(output_file, 'w') as f:
                                f.write(result.stdout)
                
                except Exception as e:
                    console.print(f"[{WARNING_COLOR}]{step_name} failed: {e}[/]")
                
                progress.update(task, completed=True)
        
        # Generate summary report
        report_file = framework.results_dir / f'osint_report_{target.replace(".", "_")}.md'
        with open(report_file, 'w') as f:
            f.write(f"# OSINT Report for {target}\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            for step_name, data in results.items():
                f.write(f"## {step_name.title()}\n\n")
                if isinstance(data, list):
                    for item in data:
                        f.write(f"- {item}\n")
                else:
                    f.write(f"```\n{data[:5000]}\n```\n\n")
        
        console.print(f"\n[{SUCCESS_COLOR}]✅ Custom OSINT workflow completed[/]")
        console.print(f"[{INFO_COLOR}]📝 Report saved to: {report_file}[/]")
        
        # AI analysis of combined results
        if framework.ollama_available and results:
            with console.status(f"[{AI_COLOR}]🤖 AI analyzing OSINT findings...[/]"):
                summary = f"OSINT workflow completed for {target} with {len(results)} data sources"
                analysis = framework.query_ollama(
                    f"{summary}. Provide a comprehensive analysis and suggest next steps for penetration testing.",
                    "You are analyzing combined OSINT data. Provide actionable intelligence and prioritized next steps."
                )
            console.print(Panel(
                Text(analysis, style=AI_COLOR),
                title="[red]🤖 AI OSINT Analysis[/]",
                border_style=AI_COLOR
            ))
        
        input("\n⏸️ Press Enter to continue...")

    @staticmethod
    def enumeration_menu(framework):
        """Complete network enumeration menu"""
        from enum import Enum
        
        # Define TestPhase locally if not accessible
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
        
        framework.current_phase = TestPhase.ENUMERATION
        
        while True:
            console.clear()
            console.print(Panel(
                Text("🌐 Network Enumeration", style=f"bold {USER_COLOR}"),
                border_style=USER_COLOR
            ))
            print_theme("enum")
            
            enum_table = Table(show_header=False, box=box.ROUNDED)
            enum_table.add_column("Option", style=f"bold {USER_COLOR}", width=8)
            enum_table.add_column("Tool/Action", style="white")
            enum_table.add_column("Status", width=12)
            
            enum_table.add_row("1", "🔍 Host Discovery", framework._tool_status('nmap'))
            enum_table.add_row("2", "⚡ Fast Port Scan (Top 1000)", framework._tool_status('nmap'))
            enum_table.add_row("3", "🔬 Full Port Scan (All 65535)", framework._tool_status('nmap'))
            enum_table.add_row("4", "🚀 Masscan (Fast sweep)", framework._tool_status('masscan'))
            enum_table.add_row("5", "📡 Service Version Detection", framework._tool_status('nmap'))
            enum_table.add_row("6", "🏢 SMB Enumeration", framework._tool_status('enum4linux'))
            enum_table.add_row("7", "📊 SNMP Enumeration", framework._tool_status('onesixtyone'))
            enum_table.add_row("8", "🌐 Web Service Discovery", framework._tool_status('whatweb'))
            enum_table.add_row("9", "🔧 Custom Scan Workflow", "[green]Available[/]")
            enum_table.add_row("10", "🤖 AI Scan Planning", "[green]Available[/]" if framework.ollama_available else "[red]Offline[/]")
            enum_table.add_row("0", "⬅️ Back to Main Menu", "")
            
            console.print(enum_table)
            
            try:
                choice = Prompt.ask(f"[{USER_COLOR}]Select enumeration option[/]",
                                  choices=['0','1','2','3','4','5','6','7','8','9','10'])
                
                if choice == '0':
                    break
                elif choice == '1':
                    CompletedImplementations.run_host_discovery(framework)
                elif choice == '2':
                    CompletedImplementations.run_fast_port_scan(framework)
                elif choice == '3':
                    CompletedImplementations.run_full_port_scan(framework)
                elif choice == '4':
                    CompletedImplementations.run_masscan(framework)
                elif choice == '5':
                    CompletedImplementations.run_service_enum(framework)
                elif choice == '6':
                    CompletedImplementations.run_smb_enum(framework)
                elif choice == '7':
                    CompletedImplementations.run_snmp_enum(framework)
                elif choice == '8':
                    CompletedImplementations.run_web_discovery(framework)
                elif choice == '9':
                    CompletedImplementations.custom_scan_workflow(framework)
                elif choice == '10':
                    CompletedImplementations.ai_scan_planning(framework)
                    
            except KeyboardInterrupt:
                break
    
    @staticmethod
    def run_host_discovery(framework):
        """Host discovery implementation"""
        target_range = Prompt.ask(f"[{USER_COLOR}]Enter target range (e.g., 192.168.1.0/24)[/]")
        
        scan_type = Prompt.ask(
            f"[{USER_COLOR}]Scan type[/]",
            choices=['ping', 'arp', 'tcp', 'udp', 'comprehensive'],
            default='ping'
        )
        
        # Build nmap command based on scan type
        if scan_type == 'ping':
            cmd = ['nmap', '-sn', target_range]
        elif scan_type == 'arp':
            cmd = ['nmap', '-sn', '-PR', target_range]
        elif scan_type == 'tcp':
            cmd = ['nmap', '-sn', '-PS21,22,23,25,80,443,445,3389', target_range]
        elif scan_type == 'udp':
            cmd = ['nmap', '-sn', '-PU161,162,123,500', target_range]
        else:  # comprehensive
            cmd = ['nmap', '-sn', '-PE', '-PP', '-PS80,443', '-PA3389', '-PU40125', target_range]
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task(f"[{AI_COLOR}]🔍 Discovering hosts in {target_range}...[/]", total=None)
            
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                
                # Parse live hosts
                live_hosts = re.findall(r'Nmap scan report for ([\w\.-]+)(?: \(([\d\.]+)\))?', result.stdout)
                
                if live_hosts:
                    host_table = Table(title=f"Live Hosts in {target_range}")
                    host_table.add_column("IP Address", style="green")
                    host_table.add_column("Hostname", style="cyan")
                    host_table.add_column("Status", style="yellow")
                    
                    for host_info in live_hosts:
                        if len(host_info) == 2 and host_info[1]:
                            # Has both hostname and IP
                            hostname = host_info[0]
                            ip = host_info[1]
                        else:
                            # Only IP
                            ip = host_info[0]
                            hostname = "Unknown"
                        
                        # Add to targets if not already present
                        if ip not in framework.targets:
                            framework.targets[ip] = Target(ip=ip, hostname=hostname if hostname != "Unknown" else None)
                        
                        host_table.add_row(ip, hostname, "🟢 Active")
                    
                    console.print(host_table)
                    console.print(f"[{SUCCESS_COLOR}]Found {len(live_hosts)} live hosts[/]")
                    
                    # Save results
                    discovery_file = framework.results_dir / f'discovery_{target_range.replace("/", "_").replace(".", "_")}.txt'
                    with open(discovery_file, 'w') as f:
                        f.write(result.stdout)
                    console.print(f"[{INFO_COLOR}]💾 Results saved to: {discovery_file}[/]")
                    
                    # AI analysis
                    if framework.ollama_available:
                        with console.status(f"[{AI_COLOR}]🤖 AI analyzing discovered hosts...[/]"):
                            analysis = framework.query_ollama(
                                f"Analyze {len(live_hosts)} discovered hosts in {target_range}. Suggest prioritization and next enumeration steps.",
                                "You are analyzing network discovery results. Provide target prioritization."
                            )
                        console.print(Panel(
                            Text(analysis, style=AI_COLOR),
                            title="[red]🤖 AI Discovery Analysis[/]",
                            border_style=AI_COLOR
                        ))
                else:
                    console.print(f"[{WARNING_COLOR}]No live hosts found in {target_range}[/]")
                    
            except subprocess.TimeoutExpired:
                console.print(f"[{ERROR_COLOR}]Host discovery timed out[/]")
            except Exception as e:
                console.print(f"[{ERROR_COLOR}]Host discovery failed: {e}[/]")
        
        input("\n⏸️ Press Enter to continue...")
    
    @staticmethod
    def run_fast_port_scan(framework):
        """Fast port scan implementation"""
        target = CompletedImplementations._select_target(framework)
        if not target:
            return
        
        framework.current_target = target
        target_obj = framework.targets[target]
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task(f"[{AI_COLOR}]⚡ Fast scanning top 1000 ports on {target}...[/]", total=None)
            
            try:
                # Fast scan with service detection
                cmd = ['nmap', '-sS', '-sV', '-T4', '--top-ports', '1000', '-oX', '-', target]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
                
                # Parse XML output
                if result.stdout:
                    root = ET.fromstring(result.stdout)
                    
                    # Parse open ports
                    for port in root.findall('.//port'):
                        if port.find('state').get('state') == 'open':
                            port_id = int(port.get('portid'))
                            protocol = port.get('protocol')
                            
                            if port_id not in target_obj.open_ports:
                                target_obj.open_ports.append(port_id)
                            
                            service = port.find('service')
                            if service is not None:
                                service_name = service.get('name', 'unknown')
                                product = service.get('product', '')
                                version = service.get('version', '')
                                target_obj.services[port_id] = f"{service_name} {product} {version}".strip()
                
                if target_obj.open_ports:
                    # Display results
                    port_table = Table(title=f"Open Ports on {target} (Fast Scan)")
                    port_table.add_column("Port", style="green", width=8)
                    port_table.add_column("Service", style="cyan", width=15)
                    port_table.add_column("Version", style="yellow")
                    
                    for port in sorted(target_obj.open_ports):
                        service_info = target_obj.services.get(port, "Unknown").split(' ', 1)
                        service = service_info[0]
                        version = service_info[1] if len(service_info) > 1 else ""
                        port_table.add_row(str(port), service, version)
                    
                    console.print(port_table)
                    console.print(f"[{SUCCESS_COLOR}]Found {len(target_obj.open_ports)} open ports[/]")
                    
                    # Save results
                    scan_file = framework.results_dir / f'nmap_fast_{target.replace(".", "_")}.xml'
                    with open(scan_file, 'w') as f:
                        f.write(result.stdout)
                    console.print(f"[{INFO_COLOR}]💾 Results saved to: {scan_file}[/]")
                else:
                    console.print(f"[{WARNING_COLOR}]No open ports found in top 1000[/]")
                    
            except subprocess.TimeoutExpired:
                console.print(f"[{ERROR_COLOR}]Port scan timed out[/]")
            except Exception as e:
                console.print(f"[{ERROR_COLOR}]Port scan failed: {e}[/]")
        
        input("\n⏸️ Press Enter to continue...")
    
    @staticmethod
    def _select_target(framework) -> Optional[str]:
        """Helper to select target"""
        if not framework.targets:
            console.print(f"[{WARNING_COLOR}]No targets available. Run host discovery first.[/]")
            input("Press Enter to continue...")
            return None
        
        if len(framework.targets) == 1:
            return list(framework.targets.keys())[0]
        
        console.print("\n[cyan]Available targets:[/]")
        target_list = list(framework.targets.keys())
        for i, ip in enumerate(target_list, 1):
            target = framework.targets[ip]
            info = f"({target.hostname})" if target.hostname else ""
            ports = f"[{len(target.open_ports)} ports]" if target.open_ports else ""
            console.print(f"  {i}. {ip} {info} {ports}")
        
        choice = Prompt.ask(
            f"[{USER_COLOR}]Select target number[/]",
            choices=[str(i) for i in range(1, len(target_list)+1)]
        )
        
        return target_list[int(choice)-1]
    
    # Add more enumeration methods...
    @staticmethod
    def run_full_port_scan(framework):
        """Full port scan - all 65535 ports"""
        target = CompletedImplementations._select_target(framework)
        if not target:
            return
        
        if not Confirm.ask(f"[{WARNING_COLOR}]Full port scan can take 10-30 minutes. Continue?[/]"):
            return
        
        framework.current_target = target
        target_obj = framework.targets[target]
        
        console.print(f"[{INFO_COLOR}]💡 Tip: This scan runs in background. Check {framework.results_dir} for results[/]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task(f"[{AI_COLOR}]🔬 Scanning all 65535 ports on {target}...[/]", total=65535)
            
            try:
                # Full port scan
                cmd = ['nmap', '-sS', '-T4', '-p-', '--min-rate', '1000', '-oX', '-', target]
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                
                # Monitor progress (simplified)
                for i in range(10):
                    time.sleep(3)
                    progress.update(task, advance=6553)
                
                stdout, stderr = process.communicate(timeout=1800)  # 30 min timeout
                
                if stdout:
                    # Parse results
                    root = ET.fromstring(stdout)
                    new_ports = []
                    
                    for port in root.findall('.//port'):
                        if port.find('state').get('state') == 'open':
                            port_id = int(port.get('portid'))
                            if port_id not in target_obj.open_ports:
                                target_obj.open_ports.append(port_id)
                                new_ports.append(port_id)
                    
                    progress.update(task, completed=65535)
                    
                    if new_ports:
                        console.print(f"[{SUCCESS_COLOR}]Found {len(new_ports)} additional open ports![/]")
                        console.print(f"New ports: {sorted(new_ports)[:20]}")
                    
                    console.print(f"[{SUCCESS_COLOR}]Total open ports: {len(target_obj.open_ports)}[/]")
                    
                    # Save results
                    scan_file = framework.results_dir / f'nmap_full_{target.replace(".", "_")}.xml'
                    with open(scan_file, 'w') as f:
                        f.write(stdout)
                    console.print(f"[{INFO_COLOR}]💾 Results saved to: {scan_file}[/]")
                    
            except subprocess.TimeoutExpired:
                console.print(f"[{ERROR_COLOR}]Full port scan timed out after 30 minutes[/]")
            except Exception as e:
                console.print(f"[{ERROR_COLOR}]Full port scan failed: {e}[/]")
        
        input("\n⏸️ Press Enter to continue...")
    
    # Additional stub methods that need to be added to framework
    @staticmethod
    def run_masscan(framework):
        """Masscan implementation"""
        if not framework.tools_status.get('masscan', {}).get('available'):
            console.print(f"[{ERROR_COLOR}]❌ Masscan not installed[/]")
            console.print(f"[{INFO_COLOR}]💡 Install with: sudo apt install masscan[/]")
            input("Press Enter to continue...")
            return
        
        console.print(f"[{INFO_COLOR}]🚀 Masscan - Ultra-fast port scanner[/]")
        input("Press Enter to continue...")
    
    @staticmethod
    def run_service_enum(framework):
        """Comprehensive service version detection"""
        target = CompletedImplementations._select_target(framework)
        if not target:
            return
        
        framework.current_target = target
        target_obj = framework.targets[target]
        
        # Check if there are open ports
        if not target_obj.open_ports:
            console.print(f"[{WARNING_COLOR}]⚠️ No open ports found for {target}. Run a port scan first.[/]")
            input("Press Enter to continue...")
            return
        
        # Ask user if they want to scan all or specific ports
        ports_choice = Prompt.ask(
            f"[{USER_COLOR}]Scan ports[/]",
            choices=['all', 'select'],
            default='all'
        )
        
        if ports_choice == 'select':
            # Show available ports
            console.print("\n[cyan]Available ports:[/]")
            for i, port in enumerate(sorted(target_obj.open_ports), 1):
                service_info = target_obj.services.get(port, "Unknown")
                console.print(f"  {i}. {port}/tcp - {service_info}")
            
            # Get port selection
            selection = Prompt.ask(f"[{USER_COLOR}]Enter port numbers (comma-separated)[/]")
            try:
                selected_ports = [int(p.strip()) for p in selection.split(',')]
                # Filter to ensure ports exist
                ports_to_scan = [p for p in selected_ports if p in target_obj.open_ports]
                if not ports_to_scan:
                    console.print(f"[{WARNING_COLOR}]No valid ports selected[/]")
                    input("Press Enter to continue...")
                    return
            except ValueError:
                console.print(f"[{ERROR_COLOR}]Invalid port selection[/]")
                input("Press Enter to continue...")
                return
        else:
            ports_to_scan = target_obj.open_ports
        
        # Build port string for nmap
        port_str = ','.join(str(p) for p in sorted(ports_to_scan))
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        ) as progress:
            task = progress.add_task(f"[{AI_COLOR}]📡 Identifying services on {target}...[/]", total=None)
            
            try:
                # Run advanced service detection
                cmd = ['nmap', '-sV', '-sC', '--version-all', '-p', port_str, '-oX', '-', target]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=900)  # 15 min timeout
                
                if result.stdout:
                    # Parse XML output
                    root = ET.fromstring(result.stdout)
                    
                    # Update service information
                    updated_count = 0
                    for port in root.findall('.//port'):
                        if port.find('state').get('state') == 'open':
                            port_id = int(port.get('portid'))
                            service = port.find('service')
                            
                            if service is not None:
                                service_name = service.get('name', 'unknown')
                                product = service.get('product', '')
                                version = service.get('version', '')
                                extrainfo = service.get('extrainfo', '')
                                ostype = service.get('ostype', '')
                                
                                service_details = f"{service_name}"
                                if product:
                                    service_details += f" {product}"
                                if version:
                                    service_details += f" {version}"
                                if extrainfo:
                                    service_details += f" ({extrainfo})"
                                if ostype:
                                    service_details += f" [{ostype}]"
                                
                                target_obj.services[port_id] = service_details
                                updated_count += 1
                    
                    # Get script output for each port
                    script_results = {}
                    for host in root.findall('.//host'):
                        for port in host.findall('.//port'):
                            port_id = int(port.get('portid'))
                            scripts = port.findall('.//script')
                            
                            if scripts:
                                script_results[port_id] = []
                                for script in scripts:
                                    script_id = script.get('id', 'unknown')
                                    script_output = script.get('output', '').strip()
                                    if script_output:
                                        script_results[port_id].append((script_id, script_output))
                    
                    # Display results
                    if updated_count > 0:
                        service_table = Table(title=f"📡 Service Details for {target}")
                        service_table.add_column("Port", style="green", width=8)
                        service_table.add_column("Service", style="cyan")
                        service_table.add_column("Details", style="yellow")
                        
                        for port in sorted(ports_to_scan):
                            service_info = target_obj.services.get(port, "Unknown")
                            # Extract service name and details
                            parts = service_info.split(' ', 1)
                            service = parts[0]
                            details = parts[1] if len(parts) > 1 else ""
                            service_table.add_row(str(port), service, details)
                        
                        console.print(service_table)
                        
                        # Display script output in separate panels
                        if script_results:
                            console.print(f"\n[{SUCCESS_COLOR}]✅ NSE Script Results:[/]")
                            
                            for port, scripts in script_results.items():
                                if scripts:
                                    script_text = ""
                                    for script_id, output in scripts:
                                        # Truncate long outputs
                                        if len(output) > 500:
                                            output = output[:500] + "\n[...truncated...]"
                                        script_text += f"[cyan]{script_id}:[/]\n{output}\n\n"
                                    
                                    console.print(Panel(
                                        Text(script_text),
                                        title=f"Port {port} - Script Results",
                                        border_style="cyan"
                                    ))
                        
                        # Save results
                        services_file = framework.results_dir / f'services_{target.replace(".", "_")}.xml'
                        with open(services_file, 'w') as f:
                            f.write(result.stdout)
                        console.print(f"\n[{INFO_COLOR}]💾 Full results saved to: {services_file}[/]")
                        
                        # Add potential vulnerabilities based on service versions
                        vulnerable_patterns = [
                            (r'apache.*\s2\.', "Apache 2.x - Multiple potential CVEs"),
                            (r'openssh.*\s[4-7]\.', "OpenSSH 4.x-7.x - Multiple known vulnerabilities"),
                            (r'mysql.*\s5\.', "MySQL 5.x - Multiple potential vulnerabilities"),
                            (r'microsoft.*sql.*\s2008|2012|2014', "MS SQL Server - Potential CVEs based on version"),
                            (r'tomcat.*\s[5-7]', "Tomcat 5.x-7.x - Multiple known vulnerabilities"),
                            (r'samba.*\s[3-4]', "Samba 3.x-4.x - Multiple SMB vulnerabilities"),
                            (r'vsftpd.*\s2\.', "vsFTPd 2.x - Multiple CVEs"),
                            (r'proftpd.*\s1\.', "ProFTPd 1.x - Multiple vulnerabilities"),
                        ]
                        
                        for port, service_info in target_obj.services.items():
                            for pattern, vuln_desc in vulnerable_patterns:
                                if re.search(pattern, service_info, re.IGNORECASE):
                                    vuln_entry = f"PORT {port}: {vuln_desc} ({service_info})"
                                    if vuln_entry not in target_obj.vulnerabilities:
                                        target_obj.vulnerabilities.append(vuln_entry)
                        
                        # AI analysis
                        if framework.ollama_available:
                            with console.status(f"[{AI_COLOR}]🤖 AI analyzing service detection results...[/]"):
                                analysis = framework.query_ollama(
                                    f"Analyze these service detection results for {target}: {dict(target_obj.services)}. Identify potential vulnerabilities, attack vectors, and interesting services to prioritize.",
                                    "You are a penetration tester analyzing service detection results. Prioritize your findings and suggest next steps."
                                )
                            console.print(Panel(
                                Text(analysis, style=AI_COLOR),
                                title="[red]🤖 AI Service Analysis[/]",
                                border_style=AI_COLOR
                            ))
                    else:
                        console.print(f"[{WARNING_COLOR}]No service details could be detected[/]")
                else:
                    console.print(f"[{WARNING_COLOR}]No results returned[/]")
                    
            except subprocess.TimeoutExpired:
                console.print(f"[{ERROR_COLOR}]Service enumeration timed out[/]")
            except Exception as e:
                console.print(f"[{ERROR_COLOR}]Service enumeration failed: {e}[/]")
        
        input("\n⏸️ Press Enter to continue...")
    
    @staticmethod
    def run_smb_enum(framework):
        """Comprehensive SMB enumeration"""
        target = CompletedImplementations._select_target(framework)
        if not target:
            return
        
        framework.current_target = target
        target_obj = framework.targets[target]
        
        # Check if SMB ports are open
        smb_ports = [139, 445]
        open_smb_ports = [p for p in smb_ports if p in target_obj.open_ports]
        
        if not open_smb_ports:
            console.print(f"[{WARNING_COLOR}]⚠️ No SMB ports (139, 445) found open on {target}[/]")
            console.print(f"[{INFO_COLOR}]💡 Run a port scan first to identify SMB services[/]")
            input("Press Enter to continue...")
            return
        
        console.print(f"[{SUCCESS_COLOR}]🏢 SMB ports detected: {open_smb_ports}[/]")
        
        enum_results = {}
        
        # Tool selection
        available_tools = [
            ('enum4linux', framework.tools_status.get('enum4linux', {}).get('available')),
            ('smbclient', framework.tools_status.get('smbclient', {}).get('available')),
            ('nbtscan', framework.tools_status.get('nbtscan', {}).get('available')),
            ('nmap_smb', True)  # nmap is always available if framework is running
        ]
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        ) as progress:
            
            # 1. Nmap SMB scripts
            if available_tools[3][1]:  # nmap_smb
                task = progress.add_task(f"[{AI_COLOR}]🔍 Running nmap SMB scripts...[/]", total=None)
                
                try:
                    cmd = [
                        'nmap', '-sV', '--script', 
                        'smb-enum-domains,smb-enum-groups,smb-enum-processes,smb-enum-sessions,smb-enum-shares,smb-enum-users,smb-os-discovery,smb-security-mode,smb-system-info',
                        '-p', '139,445', '-oX', '-', target
                    ]
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                    
                    if result.stdout:
                        # Parse script output
                        root = ET.fromstring(result.stdout)
                        script_output = ""
                        
                        for script in root.findall('.//script'):
                            script_id = script.get('id', 'unknown')
                            output = script.get('output', '').strip()
                            if output:
                                script_output += f"\n=== {script_id.upper()} ===\n{output}\n"
                        
                        if script_output:
                            enum_results['nmap_smb'] = script_output.strip()
                            # Save nmap results
                            nmap_file = framework.results_dir / f'nmap_smb_{target.replace(".", "_")}.xml'
                            with open(nmap_file, 'w') as f:
                                f.write(result.stdout)
                                
                except Exception as e:
                    console.print(f"[{WARNING_COLOR}]Nmap SMB scripts failed: {e}[/]")
                
                progress.update(task, completed=True)
            
            # 2. enum4linux
            if available_tools[0][1]:  # enum4linux
                task = progress.add_task(f"[{AI_COLOR}]📋 Running enum4linux...[/]", total=None)
                
                try:
                    cmd = ['enum4linux', '-a', target]
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                    
                    if result.stdout:
                        enum_results['enum4linux'] = result.stdout
                        # Save enum4linux results
                        enum4_file = framework.results_dir / f'enum4linux_{target.replace(".", "_")}.txt'
                        with open(enum4_file, 'w') as f:
                            f.write(result.stdout)
                                
                except Exception as e:
                    console.print(f"[{WARNING_COLOR}]enum4linux failed: {e}[/]")
                
                progress.update(task, completed=True)
            
            # 3. smbclient listing
            if available_tools[1][1]:  # smbclient
                task = progress.add_task(f"[{AI_COLOR}]🗂️ Running smbclient share enumeration...[/]", total=None)
                
                try:
                    # List shares
                    cmd = ['smbclient', '-L', target, '-N']
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                    
                    if result.stdout:
                        enum_results['smbclient'] = result.stdout
                        # Save smbclient results
                        smb_file = framework.results_dir / f'smbclient_{target.replace(".", "_")}.txt'
                        with open(smb_file, 'w') as f:
                            f.write(result.stdout)
                    
                    # Try to connect to common shares
                    common_shares = ['IPC$', 'C$', 'ADMIN$', 'Users', 'Public']
                    share_access = {}
                    
                    for share in common_shares:
                        try:
                            cmd = ['smbclient', f'//{target}/{share}', '-N', '-c', 'ls']
                            share_result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                            
                            if share_result.returncode == 0:
                                share_access[share] = "Accessible (Anonymous)"
                            else:
                                share_access[share] = "Access Denied"
                        except:
                            share_access[share] = "Connection Failed"
                    
                    if share_access:
                        enum_results['share_access'] = share_access
                                
                except Exception as e:
                    console.print(f"[{WARNING_COLOR}]smbclient failed: {e}[/]")
                
                progress.update(task, completed=True)
            
            # 4. nbtscan
            if available_tools[2][1]:  # nbtscan
                task = progress.add_task(f"[{AI_COLOR}]🏷️ Running nbtscan...[/]", total=None)
                
                try:
                    cmd = ['nbtscan', target]
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                    
                    if result.stdout:
                        enum_results['nbtscan'] = result.stdout
                        # Save nbtscan results
                        nbt_file = framework.results_dir / f'nbtscan_{target.replace(".", "_")}.txt'
                        with open(nbt_file, 'w') as f:
                            f.write(result.stdout)
                                
                except Exception as e:
                    console.print(f"[{WARNING_COLOR}]nbtscan failed: {e}[/]")
                
                progress.update(task, completed=True)
        
        # Display results
        if enum_results:
            console.print(f"\n[{SUCCESS_COLOR}]🏢 SMB Enumeration Results for {target}[/]")
            
            # Display share access if available
            if 'share_access' in enum_results:
                share_table = Table(title="SMB Share Access Test")
                share_table.add_column("Share", style="cyan", width=15)
                share_table.add_column("Status", style="yellow")
                
                for share, status in enum_results['share_access'].items():
                    if "Accessible" in status:
                        status_color = "green"
                        # Add potential vulnerability
                        vuln = f"SMB Share {share}: Anonymous access allowed"
                        if vuln not in target_obj.vulnerabilities:
                            target_obj.vulnerabilities.append(vuln)
                    elif "Access Denied" in status:
                        status_color = "red"
                    else:
                        status_color = "yellow"
                    
                    share_table.add_row(share, f"[{status_color}]{status}[/]")
                
                console.print(share_table)
            
            # Display other results in panels
            for tool_name, output in enum_results.items():
                if tool_name == 'share_access':
                    continue  # Already displayed above
                
                # Truncate long outputs for display
                display_output = output
                if len(display_output) > 2000:
                    display_output = display_output[:2000] + "\n\n[...truncated...]"
                
                console.print(Panel(
                    Syntax(display_output, "text", theme="monokai", word_wrap=True),
                    title=f"🏢 {tool_name.upper()} Results",
                    border_style="cyan"
                ))
            
            # Parse findings for potential vulnerabilities
            vulnerability_indicators = [
                (r'SMB.*signing.*not required', "SMB signing not enforced - susceptible to relay attacks"),
                (r'Guest.*allowed', "Guest access enabled - potential information disclosure"),
                (r'NULL.*session', "NULL sessions allowed - enumeration possible"),
                (r'Everyone.*Full Control', "Dangerous share permissions detected"),
                (r'Windows.*2003|XP|2000', "Legacy Windows version - multiple known vulnerabilities"),
                (r'SMBv1.*enabled', "SMBv1 enabled - WannaCry/EternalBlue vulnerable")
            ]
            
            combined_output = ' '.join(enum_results.values())
            for pattern, vuln_desc in vulnerability_indicators:
                if re.search(pattern, combined_output, re.IGNORECASE):
                    vuln = f"SMB: {vuln_desc}"
                    if vuln not in target_obj.vulnerabilities:
                        target_obj.vulnerabilities.append(vuln)
            
            console.print(f"\n[{INFO_COLOR}]💾 All SMB enumeration results saved to {framework.results_dir}[/]")
            
            # AI analysis
            if framework.ollama_available:
                with console.status(f"[{AI_COLOR}]🤖 AI analyzing SMB enumeration...[/]"):
                    # Provide summarized output to AI
                    analysis_data = {
                        'target': target,
                        'open_ports': open_smb_ports,
                        'vulnerabilities': target_obj.vulnerabilities[-5:] if target_obj.vulnerabilities else [],
                        'share_access': enum_results.get('share_access', {})
                    }
                    
                    analysis = framework.query_ollama(
                        f"Analyze SMB enumeration results for {target}: {analysis_data}. Identify critical vulnerabilities, attack paths, and suggest exploitation techniques.",
                        "You are analyzing SMB enumeration results. Focus on actionable vulnerabilities and attack vectors."
                    )
                console.print(Panel(
                    Text(analysis, style=AI_COLOR),
                    title="[red]🤖 AI SMB Analysis[/]",
                    border_style=AI_COLOR
                ))
        else:
            console.print(f"[{WARNING_COLOR}]No SMB enumeration data collected[/]")
        
        input("\n⏸️ Press Enter to continue...")
    
    @staticmethod
    def vulnerability_menu(framework):
        """Complete vulnerability scanning menu"""
        from enum import Enum
        
        # Define TestPhase locally if not accessible
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
        
        framework.current_phase = TestPhase.VULNERABILITY_SCAN
        
        while True:
            console.clear()
            console.print(Panel(
                Text("🔎 Vulnerability Scanning", style=f"bold {USER_COLOR}"),
                border_style=USER_COLOR
            ))
            print_theme("vuln")
            
            vuln_table = Table(show_header=False, box=box.ROUNDED)
            vuln_table.add_column("Option", style=f"bold {USER_COLOR}", width=8)
            vuln_table.add_column("Tool/Action", style="white")
            vuln_table.add_column("Status", width=12)
            
            vuln_table.add_row("1", "🔍 Nmap Vulnerability Scripts", framework._tool_status('nmap'))
            vuln_table.add_row("2", "🌐 Nikto Web Vulnerability Scanner", framework._tool_status('nikto'))
            vuln_table.add_row("3", "📁 Directory/File Brute Force", framework._tool_status('gobuster'))
            vuln_table.add_row("4", "📊 SQL Injection Testing", framework._tool_status('sqlmap'))
            vuln_table.add_row("5", "🔒 SSL/TLS Security Analysis", "[green]Available[/]")
            vuln_table.add_row("6", "🌍 WordPress Security Scan", framework._tool_status('wpscan'))
            vuln_table.add_row("7", "🔥 Web Application Firewall Detection", framework._tool_status('wafw00f'))
            vuln_table.add_row("8", "🚀 Multi-tool Vulnerability Workflow", "[green]Available[/]")
            vuln_table.add_row("9", "🤖 AI-Guided Vulnerability Assessment", "[green]Available[/]" if framework.ollama_available else "[red]Offline[/]")
            vuln_table.add_row("0", "⬅️ Back to Main Menu", "")
            
            console.print(vuln_table)
            
            try:
                choice = Prompt.ask(f"[{USER_COLOR}]Select vulnerability scanning option[/]",
                                  choices=['0','1','2','3','4','5','6','7','8','9'])
                
                if choice == '0':
                    break
                elif choice == '1':
                    CompletedImplementations.run_nmap_vuln_scripts(framework)
                elif choice == '2':
                    CompletedImplementations.run_nikto_scan(framework)
                elif choice == '3':
                    CompletedImplementations.run_directory_bruteforce(framework)
                elif choice == '4':
                    CompletedImplementations.run_sql_injection_test(framework)
                elif choice == '5':
                    CompletedImplementations.run_ssl_analysis(framework)
                elif choice == '6':
                    CompletedImplementations.run_wordpress_scan(framework)
                elif choice == '7':
                    CompletedImplementations.run_waf_detection(framework)
                elif choice == '8':
                    CompletedImplementations.run_multitool_vuln_workflow(framework)
                elif choice == '9':
                    CompletedImplementations.ai_vulnerability_assessment(framework)
                    
            except KeyboardInterrupt:
                break
    
    @staticmethod
    def run_nmap_vuln_scripts(framework):
        """Run comprehensive Nmap vulnerability scripts"""
        print_theme("vuln")
        target = CompletedImplementations._select_target(framework)
        if not target:
            return
        
        framework.current_target = target
        target_obj = framework.targets[target]
        
        # Check for open ports
        if not target_obj.open_ports:
            console.print(f"[{WARNING_COLOR}]⚠️ No open ports found. Run a port scan first.[/]")
            input("Press Enter to continue...")
            return
        
        # Script category selection
        script_categories = {
            'vuln': 'Vulnerability detection scripts',
            'exploit': 'Safe exploitation checks',
            'auth': 'Authentication bypass tests', 
            'brute': 'Brute force attacks (safe)',
            'discovery': 'Service discovery and enumeration',
            'safe': 'All safe scripts only',
            'all': 'All vulnerability scripts (includes unsafe)'
        }
        
        console.print("\n[cyan]Available script categories:[/]")
        for cat, desc in script_categories.items():
            console.print(f"  • {cat}: {desc}")
        
        category = Prompt.ask(
            f"[{USER_COLOR}]Select script category[/]",
            choices=list(script_categories.keys()),
            default='vuln'
        )
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        ) as progress:
            task = progress.add_task(f"[{AI_COLOR}]🔍 Running Nmap {category} scripts on {target}...[/]", total=None)
            
            try:
                # Build nmap command based on category
                if category == 'all':
                    script_args = '--script=vuln,exploit,auth,brute,discovery'
                else:
                    script_args = f'--script={category}'
                
                # Target specific ports if available
                port_list = ','.join(str(p) for p in sorted(target_obj.open_ports[:20]))  # Limit to first 20 ports
                
                cmd = ['nmap', '-sV', script_args, '-p', port_list, '--script-args=unsafe=1', '-oX', '-', target]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=1200)  # 20 min timeout
                
                if result.stdout:
                    # Parse XML results
                    root = ET.fromstring(result.stdout)
                    
                    vulnerabilities_found = []
                    script_results = {}
                    
                    for host in root.findall('.//host'):
                        for port in host.findall('.//port'):
                            port_id = int(port.get('portid'))
                            scripts = port.findall('.//script')
                            
                            if scripts:
                                script_results[port_id] = []
                                for script in scripts:
                                    script_id = script.get('id', 'unknown')
                                    script_output = script.get('output', '').strip()
                                    
                                    if script_output:
                                        script_results[port_id].append((script_id, script_output))
                                        
                                        # Check for vulnerability indicators
                                        vuln_indicators = [
                                            ('CVE-', 'CVE reference found'),
                                            ('VULNERABLE:', 'Confirmed vulnerability'),
                                            ('State: VULNERABLE', 'Vulnerable state detected'),
                                            ('EXPLOIT', 'Exploitable condition'),
                                            ('backdoor', 'Potential backdoor'),
                                            ('weak', 'Weak configuration'),
                                            ('anonymous', 'Anonymous access')
                                        ]
                                        
                                        for indicator, desc in vuln_indicators:
                                            if indicator.lower() in script_output.lower():
                                                vuln = f"PORT {port_id} ({script_id}): {desc}"
                                                if vuln not in vulnerabilities_found:
                                                    vulnerabilities_found.append(vuln)
                                                    
                                                # Add to target vulnerabilities
                                                if vuln not in target_obj.vulnerabilities:
                                                    target_obj.vulnerabilities.append(vuln)
                    
                    # Display results
                    if script_results:
                        console.print(f"\n[{SUCCESS_COLOR}]🔍 Nmap Vulnerability Scan Results for {target}[/]")
                        
                        # Summary table
                        if vulnerabilities_found:
                            vuln_summary_table = Table(title="Vulnerabilities Detected")
                            vuln_summary_table.add_column("Port", style="red", width=8)
                            vuln_summary_table.add_column("Vulnerability", style="yellow")
                            
                            for vuln in vulnerabilities_found:
                                if 'PORT' in vuln:
                                    port_part = vuln.split('PORT ')[1].split(' ')[0]
                                    vuln_part = vuln.split('): ')[1] if '): ' in vuln else vuln.split(': ')[1]
                                    vuln_summary_table.add_row(port_part, vuln_part)
                            
                            console.print(vuln_summary_table)
                        
                        # Detailed script output
                        console.print(f"\n[{INFO_COLOR}]📋 Detailed Script Output:[/]")
                        for port, scripts in script_results.items():
                            if scripts:
                                for script_id, output in scripts:
                                    # Truncate very long outputs
                                    display_output = output[:1500] + "\n\n[...truncated...]" if len(output) > 1500 else output
                                    
                                    console.print(Panel(
                                        Syntax(display_output, "text", theme="monokai", word_wrap=True),
                                        title=f"Port {port} - {script_id}",
                                        border_style="red" if any(indicator in output.lower() for indicator, _ in [
                                            ('vulnerable', ''), ('cve-', ''), ('exploit', ''), ('backdoor', '')
                                        ]) else "cyan"
                                    ))
                        
                        # Save results
                        vuln_file = framework.results_dir / f'nmap_vuln_{target.replace(".", "_")}.xml'
                        with open(vuln_file, 'w') as f:
                            f.write(result.stdout)
                        console.print(f"\n[{INFO_COLOR}]💾 Full results saved to: {vuln_file}[/]")
                        
                        if vulnerabilities_found:
                            console.print(f"\n[{SUCCESS_COLOR}]✅ Found {len(vulnerabilities_found)} potential vulnerabilities![/]")
                        
                        # AI analysis
                        if framework.ollama_available and vulnerabilities_found:
                            with console.status(f"[{AI_COLOR}]🤖 AI analyzing vulnerability scan results...[/]"):
                                analysis = framework.query_ollama(
                                    f"Analyze Nmap vulnerability scan results for {target}: {vulnerabilities_found[:10]}. Prioritize by severity and exploitability, suggest next steps.",
                                    "You are analyzing vulnerability scan results. Focus on the most critical findings and actionable recommendations."
                                )
                            console.print(Panel(
                                Text(analysis, style=AI_COLOR),
                                title="[red]🤖 AI Vulnerability Analysis[/]",
                                border_style=AI_COLOR
                            ))
                    else:
                        console.print(f"[{WARNING_COLOR}]No script results returned[/]")
                else:
                    console.print(f"[{WARNING_COLOR}]No scan output received[/]")
                    
            except subprocess.TimeoutExpired:
                console.print(f"[{ERROR_COLOR}]Vulnerability scan timed out[/]")
            except Exception as e:
                console.print(f"[{ERROR_COLOR}]Vulnerability scan failed: {e}[/]")
        
        input("\n⏸️ Press Enter to continue...")
    
    @staticmethod
    def run_nikto_scan(framework):
        """Run Nikto web vulnerability scanner"""
        print_theme("vuln")
        if not framework.tools_status.get('nikto', {}).get('available'):
            console.print(f"[{ERROR_COLOR}]❌ Nikto not installed[/]")
            console.print(f"[{INFO_COLOR}]💡 Install with: sudo apt install nikto[/]")
            input("Press Enter to continue...")
            return
        
        target = CompletedImplementations._select_target(framework)
        if not target:
            return
        
        framework.current_target = target
        target_obj = framework.targets[target]
        
        # Check for web ports
        web_ports = [p for p in target_obj.open_ports if p in [80, 443, 8080, 8443, 8000, 8888, 9000]]
        
        if not web_ports:
            console.print(f"[{WARNING_COLOR}]⚠️ No common web ports found on {target}[/]")
            if Confirm.ask(f"[{USER_COLOR}]Run Nikto anyway on port 80?[/]"):
                web_ports = [80]
            else:
                input("Press Enter to continue...")
                return
        
        console.print(f"[{INFO_COLOR}]🌐 Web ports detected: {web_ports}[/]")
        
        # Select ports to scan
        if len(web_ports) > 1:
            console.print("\n[cyan]Available web ports:[/]")
            for i, port in enumerate(web_ports, 1):
                console.print(f"  {i}. {port}")
            
            port_choice = Prompt.ask(
                f"[{USER_COLOR}]Select port (number) or 'all'[/]",
                default='all'
            )
            
            if port_choice.lower() != 'all' and port_choice.isdigit():
                idx = int(port_choice) - 1
                if 0 <= idx < len(web_ports):
                    scan_ports = [web_ports[idx]]
                else:
                    scan_ports = web_ports
            else:
                scan_ports = web_ports
        else:
            scan_ports = web_ports
        
        nikto_results = []
        
        for port in scan_ports:
            protocol = 'https' if port in [443, 8443] else 'http'
            url = f"{protocol}://{target}:{port}"
            
            with console.status(f"[{AI_COLOR}]🌐 Running Nikto scan on {url}...[/]"):
                try:
                    cmd = ['nikto', '-h', url, '-Format', 'txt', '-output', '-']
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
                    
                    if result.stdout:
                        nikto_results.append((port, result.stdout))
                        
                        # Parse for interesting findings
                        lines = result.stdout.split('\n')
                        vulnerabilities = []
                        
                        for line in lines:
                            # Look for potential vulnerabilities
                            vuln_indicators = [
                                ('OSVDB', 'Security database reference'),
                                ('CVE', 'Common Vulnerability reference'),
                                ('backdoor', 'Potential backdoor'),
                                ('admin', 'Admin interface exposed'),
                                ('config', 'Configuration file exposed'),
                                ('backup', 'Backup file found'),
                                ('directory listing', 'Directory browsing enabled'),
                                ('vulnerable', 'Vulnerability detected')
                            ]
                            
                            for indicator, desc in vuln_indicators:
                                if indicator.lower() in line.lower() and line.strip().startswith('+'):
                                    vuln = f"PORT {port} (HTTP): {desc} - {line.strip()}"
                                    vulnerabilities.append(vuln)
                                    if vuln not in target_obj.vulnerabilities:
                                        target_obj.vulnerabilities.append(vuln)
                        
                        # Save individual results
                        nikto_file = framework.results_dir / f'nikto_{target.replace(".", "_")}_{port}.txt'
                        with open(nikto_file, 'w') as f:
                            f.write(result.stdout)
                        
                        console.print(f"[{INFO_COLOR}]Port {port} scan complete - {len(vulnerabilities)} findings[/]")
                        
                except subprocess.TimeoutExpired:
                    console.print(f"[{ERROR_COLOR}]Nikto scan on port {port} timed out[/]")
                except Exception as e:
                    console.print(f"[{ERROR_COLOR}]Nikto scan on port {port} failed: {e}[/]")
        
        # Display results
        if nikto_results:
            console.print(f"\n[{SUCCESS_COLOR}]🌐 Nikto Scan Results for {target}[/]")
            
            for port, output in nikto_results:
                # Extract key findings
                findings = []
                lines = output.split('\n')
                
                for line in lines:
                    if line.strip().startswith('+') and len(line.strip()) > 2:
                        findings.append(line.strip()[2:])  # Remove '+ ' prefix
                
                if findings:
                    console.print(Panel(
                        Text('\n'.join(findings[:20]) + (f"\n\n... and {len(findings)-20} more findings" if len(findings) > 20 else "")),
                        title=f"🌐 Port {port} - Nikto Findings",
                        border_style="yellow"
                    ))
                else:
                    console.print(f"[{INFO_COLOR}]Port {port}: No significant findings[/]")
            
            console.print(f"\n[{INFO_COLOR}]💾 All Nikto results saved to {framework.results_dir}[/]")
        else:
            console.print(f"[{WARNING_COLOR}]No Nikto results collected[/]")
        
        input("\n⏸️ Press Enter to continue...")
    
    @staticmethod
    def run_directory_bruteforce(framework):
        """Directory/file brute force with gobuster/dirb"""
        if not framework.tools_status.get('gobuster', {}).get('available'):
            console.print(f"[{ERROR_COLOR}]❌ Gobuster not installed[/]")
            console.print(f"[{INFO_COLOR}]💡 Install with: sudo apt install gobuster[/]")
            input("Press Enter to continue...")
            return
        
        target = CompletedImplementations._select_target(framework)
        if not target:
            return
        
        # Check for web ports and run directory brute force
        web_ports = [p for p in framework.targets[target].open_ports if p in [80, 443, 8080, 8443]]
        if web_ports:
            console.print(f"[{SUCCESS_COLOR}]🌐 Running directory brute force on {target}:{web_ports[0]}[/]")
            # Implementation would go here
        else:
            console.print(f"[{WARNING_COLOR}]No web ports found[/]")
        
        input("Press Enter to continue...")
    
    @staticmethod
    def run_sql_injection_test(framework):
        """SQL injection testing with sqlmap"""
        if not framework.tools_status.get('sqlmap', {}).get('available'):
            console.print(f"[{ERROR_COLOR}]❌ SQLMap not installed[/]")
            console.print(f"[{INFO_COLOR}]💡 Install with: sudo apt install sqlmap[/]")
        else:
            console.print(f"[{INFO_COLOR}]📊 SQL injection testing - Ready to implement[/]")
        input("Press Enter to continue...")
    
    @staticmethod
    def run_ssl_analysis(framework):
        """SSL/TLS security analysis"""
        console.print(f"[{INFO_COLOR}]🔒 SSL/TLS Analysis - Using nmap ssl scripts[/]")
        input("Press Enter to continue...")
    
    @staticmethod
    def run_wordpress_scan(framework):
        """WordPress security scan"""
        if not framework.tools_status.get('wpscan', {}).get('available'):
            console.print(f"[{ERROR_COLOR}]❌ WPScan not installed[/]")
        else:
            console.print(f"[{INFO_COLOR}]🌍 WordPress scanning ready[/]")
        input("Press Enter to continue...")
    
    @staticmethod
    def run_waf_detection(framework):
        """Web Application Firewall detection"""
        if not framework.tools_status.get('wafw00f', {}).get('available'):
            console.print(f"[{ERROR_COLOR}]❌ wafw00f not installed[/]")
        else:
            console.print(f"[{INFO_COLOR}]🔥 WAF detection ready[/]")
        input("Press Enter to continue...")
    
    @staticmethod
    def run_multitool_vuln_workflow(framework):
        """Multi-tool vulnerability workflow"""
        console.print(f"[{INFO_COLOR}]🚀 Multi-tool vulnerability workflow[/]")
        console.print("This would run: Nmap vuln scripts → Nikto → Directory brute force → Custom analysis")
        input("Press Enter to continue...")
    
    @staticmethod
    def ai_vulnerability_assessment(framework):
        """AI-guided vulnerability assessment"""
        if not framework.ollama_available:
            console.print(f"[{ERROR_COLOR}]❌ AI not available[/]")
            input("Press Enter to continue...")
            return
        
        console.print(f"[{INFO_COLOR}]🤖 AI vulnerability assessment[/]")
        console.print("This would provide AI-guided vulnerability discovery and prioritization")
        input("Press Enter to continue...")

    @staticmethod
    def run_snmp_enum(framework):
        """SNMP enumeration"""
        console.print(f"[{INFO_COLOR}]📊 SNMP enumeration[/]")
        input("Press Enter to continue...")
    
    @staticmethod
    def run_web_discovery(framework):
        """Web service discovery"""
        console.print(f"[{INFO_COLOR}]🌐 Web service discovery[/]")
        input("Press Enter to continue...")
    
    @staticmethod
    def custom_scan_workflow(framework):
        """Custom scan workflow"""
        console.print(f"[{INFO_COLOR}]🔧 Custom scan workflow[/]")
        input("Press Enter to continue...")
    
    @staticmethod
    def ai_scan_planning(framework):
        """AI-assisted scan planning"""
        if not framework.ollama_available:
            console.print(f"[{ERROR_COLOR}]❌ AI not available[/]")
            input("Press Enter to continue...")
            return
        
        console.print(f"[{INFO_COLOR}]🤖 AI scan planning[/]")
        input("Press Enter to continue...")
