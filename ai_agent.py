#!/usr/bin/env python3
"""
REDEYESdontcry AI Agent Controller
Autonomous AI-driven penetration testing operations
"""

import json
import subprocess
import time
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
import asyncio
from concurrent.futures import ThreadPoolExecutor
import threading

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.live import Live
from rich.table import Table
from rich.align import Align

console = Console()

class AIAgent:
    """Autonomous AI agent for penetration testing operations"""
    
    def __init__(self, framework):
        self.framework = framework
        self.console = Console()
        self.operations_log = []
        self.current_operation = None
        self.autonomous_mode = False
        self.executor = ThreadPoolExecutor(max_workers=5)
        
    def enable_autonomous_mode(self):
        """Enable fully autonomous operation mode"""
        self.autonomous_mode = True
        self.console.print(Panel(
            Text("🤖 AUTONOMOUS AI AGENT ACTIVATED", style="bold red"),
            subtitle="AI will now perform autonomous red team operations",
            border_style="red"
        ))
    
    async def execute_autonomous_redteam(self, target: str, scope: List[str] = None):
        """Execute complete autonomous red team engagement"""
        if not self.framework.ollama_available:
            self.console.print("[red]❌ AI not available - autonomous mode requires Ollama[/]")
            return
        
        self.console.print(Panel(
            f"🎯 Starting Autonomous Red Team Operation\nTarget: {target}",
            title="[bold red]👁️ REDEYESdontcry AI Agent[/]",
            border_style="red"
        ))
        
        # Phase 1: AI Planning
        await self._ai_planning_phase(target, scope)
        
        # Phase 2: OSINT & Reconnaissance
        await self._autonomous_osint_phase(target)
        
        # Phase 3: Network Enumeration
        await self._autonomous_enumeration_phase()
        
        # Phase 4: Vulnerability Assessment
        await self._autonomous_vulnerability_phase()
        
        # Phase 5: Exploitation
        await self._autonomous_exploitation_phase()
        
        # Phase 6: Post-Exploitation
        await self._autonomous_post_exploitation_phase()
        
        # Phase 7: Reporting
        await self._autonomous_reporting_phase()
    
    async def _ai_planning_phase(self, target: str, scope: List[str]):
        """AI analyzes target and creates attack plan"""
        with Live(self._create_status_panel("🧠 AI Strategic Planning", "Analyzing target and creating attack strategy..."), refresh_per_second=4):
            time.sleep(2)  # Simulate AI thinking
            
            plan_prompt = f"""
            Target: {target}
            Scope: {scope or ['Full authorized assessment']}
            
            Create a comprehensive penetration testing plan including:
            1. OSINT reconnaissance strategy
            2. Network enumeration approach
            3. Vulnerability assessment priorities
            4. Potential exploitation vectors
            5. Post-exploitation objectives
            6. Risk assessment and safety measures
            
            Provide specific tools and techniques for each phase.
            """
            
            ai_plan = self.framework.query_ollama(
                plan_prompt,
                "You are an expert red team leader creating a comprehensive penetration testing strategy. Be specific about tools, techniques, and priorities."
            )
            
            self.operations_log.append({
                'phase': 'planning',
                'timestamp': time.time(),
                'ai_plan': ai_plan,
                'target': target,
                'scope': scope
            })
            
            self.console.print(Panel(
                Text(ai_plan[:500] + "..." if len(ai_plan) > 500 else ai_plan, style="cyan"),
                title="[bold red]🧠 AI Attack Plan[/]",
                border_style="red"
            ))
    
    async def _autonomous_osint_phase(self, target: str):
        """AI-driven OSINT and reconnaissance"""
        self.current_operation = "OSINT & Reconnaissance"
        
        with Live(self._create_status_panel("🔍 Autonomous OSINT", "AI executing reconnaissance operations..."), refresh_per_second=2):
            # AI decides which OSINT tools to use
            osint_strategy = self.framework.query_ollama(
                f"Target: {target}. Which OSINT tools should I run and in what order? Consider: whois, DNS recon, subdomain enum, email harvesting, Shodan, social media.",
                "You are executing OSINT. Provide a prioritized list of specific commands and tools."
            )
            
            # Extract and execute OSINT commands
            commands = self._extract_commands_from_ai(osint_strategy)
            
            for cmd in commands[:5]:  # Execute top 5 OSINT operations
                try:
                    await self._execute_tool_autonomously(cmd, "OSINT")
                except Exception as e:
                    self.console.print(f"[yellow]⚠️ OSINT command failed: {cmd} - {e}[/]")
            
            # AI analyzes OSINT results
            await self._ai_analyze_phase_results("OSINT")
    
    async def _autonomous_enumeration_phase(self):
        """AI-driven network enumeration"""
        self.current_operation = "Network Enumeration"
        
        if not self.framework.targets:
            self.console.print("[yellow]⚠️ No targets identified from OSINT, using original target[/]")
            return
        
        with Live(self._create_status_panel("🌐 Network Enumeration", "AI scanning network infrastructure..."), refresh_per_second=2):
            for target_ip in list(self.framework.targets.keys())[:3]:  # Limit to first 3 targets
                enum_strategy = self.framework.query_ollama(
                    f"Target IP: {target_ip}. Plan network enumeration: port scanning, service detection, SMB enum, SNMP enum. What's the optimal scanning strategy?",
                    "You are performing network enumeration. Provide specific nmap commands and enumeration techniques."
                )
                
                commands = self._extract_commands_from_ai(enum_strategy)
                
                for cmd in commands[:4]:  # Execute top 4 enum operations per target
                    try:
                        await self._execute_tool_autonomously(cmd, "ENUMERATION", target_ip)
                    except Exception as e:
                        self.console.print(f"[yellow]⚠️ Enum command failed: {cmd} - {e}[/]")
            
            await self._ai_analyze_phase_results("ENUMERATION")
    
    async def _autonomous_vulnerability_phase(self):
        """AI-driven vulnerability assessment"""
        self.current_operation = "Vulnerability Assessment"
        
        with Live(self._create_status_panel("🔎 Vulnerability Assessment", "AI identifying security weaknesses..."), refresh_per_second=2):
            for target_ip, target_obj in self.framework.targets.items():
                if not target_obj.open_ports:
                    continue
                
                vuln_strategy = self.framework.query_ollama(
                    f"Target: {target_ip}, Open ports: {target_obj.open_ports[:10]}, Services: {dict(list(target_obj.services.items())[:5])}. Plan vulnerability assessment: NSE scripts, Nikto, directory brute force, etc.",
                    "You are conducting vulnerability assessment. Provide specific vulnerability scanning commands."
                )
                
                commands = self._extract_commands_from_ai(vuln_strategy)
                
                for cmd in commands[:3]:  # Execute top 3 vuln scans per target
                    try:
                        await self._execute_tool_autonomously(cmd, "VULNERABILITY", target_ip)
                    except Exception as e:
                        self.console.print(f"[yellow]⚠️ Vuln command failed: {cmd} - {e}[/]")
            
            await self._ai_analyze_phase_results("VULNERABILITY")
    
    async def _autonomous_exploitation_phase(self):
        """AI-driven exploitation using Metasploit and other tools"""
        self.current_operation = "Exploitation"
        
        # Check for vulnerabilities to exploit
        exploitable_targets = {}
        for target_ip, target_obj in self.framework.targets.items():
            if target_obj.vulnerabilities:
                exploitable_targets[target_ip] = target_obj.vulnerabilities
        
        if not exploitable_targets:
            self.console.print("[yellow]⚠️ No clear vulnerabilities identified for exploitation[/]")
            return
        
        with Live(self._create_status_panel("💥 Autonomous Exploitation", "AI attempting to compromise targets..."), refresh_per_second=2):
            for target_ip, vulns in exploitable_targets.items():
                exploit_strategy = self.framework.query_ollama(
                    f"Target: {target_ip}, Vulnerabilities: {vulns[:5]}. Plan exploitation using Metasploit, Hydra, or other tools. What exploits should I try?",
                    "You are conducting ethical penetration testing exploitation. Provide specific exploit commands and Metasploit modules."
                )
                
                # Extract Metasploit and exploit commands
                exploit_commands = self._extract_exploit_commands(exploit_strategy)
                
                for cmd in exploit_commands[:2]:  # Limit to 2 exploit attempts per target
                    try:
                        await self._execute_exploit_autonomously(cmd, target_ip)
                    except Exception as e:
                        self.console.print(f"[yellow]⚠️ Exploit failed: {cmd} - {e}[/]")
            
            await self._ai_analyze_phase_results("EXPLOITATION")
    
    async def _autonomous_post_exploitation_phase(self):
        """AI-driven post-exploitation activities"""
        self.current_operation = "Post-Exploitation"
        
        compromised_targets = [ip for ip, target in self.framework.targets.items() if target.exploited]
        
        if not compromised_targets:
            self.console.print("[yellow]⚠️ No targets compromised, skipping post-exploitation[/]")
            return
        
        with Live(self._create_status_panel("🔓 Post-Exploitation", "AI conducting post-exploitation activities..."), refresh_per_second=2):
            for target_ip in compromised_targets:
                postex_strategy = self.framework.query_ollama(
                    f"Compromised target: {target_ip}. Plan post-exploitation: privilege escalation, persistence, lateral movement, data gathering. What should I do next?",
                    "You are conducting post-exploitation activities. Provide specific commands for privilege escalation and data gathering."
                )
                
                postex_commands = self._extract_commands_from_ai(postex_strategy)
                
                for cmd in postex_commands[:3]:  # Limit post-ex activities
                    try:
                        await self._execute_tool_autonomously(cmd, "POST_EXPLOITATION", target_ip)
                    except Exception as e:
                        self.console.print(f"[yellow]⚠️ Post-ex command failed: {cmd} - {e}[/]")
            
            await self._ai_analyze_phase_results("POST_EXPLOITATION")
    
    async def _autonomous_reporting_phase(self):
        """AI-driven report generation and analysis"""
        self.current_operation = "Reporting & Analysis"
        
        with Live(self._create_status_panel("📊 Final Analysis", "AI generating comprehensive report..."), refresh_per_second=2):
            # AI analyzes entire engagement
            final_analysis = self.framework.query_ollama(
                f"Analyze complete penetration test results. Targets: {len(self.framework.targets)}, Total vulnerabilities: {sum(len(t.vulnerabilities) for t in self.framework.targets.values())}, Compromised: {sum(1 for t in self.framework.targets.values() if t.exploited)}. Provide executive summary and recommendations.",
                "You are creating a final penetration test report. Provide executive summary, key findings, risk assessment, and remediation recommendations."
            )
            
            # Generate enhanced report with AI insights
            self.framework.context_data['ai_final_analysis'] = final_analysis
            self.framework.generate_report()
            
            self.console.print(Panel(
                Text(final_analysis[:800] + "..." if len(final_analysis) > 800 else final_analysis, style="green"),
                title="[bold red]🎯 AI Final Assessment[/]",
                border_style="green"
            ))
        
        self.console.print(Panel(
            "[bold green]✅ AUTONOMOUS RED TEAM OPERATION COMPLETED[/]\n" +
            f"Targets Assessed: {len(self.framework.targets)}\n" +
            f"Vulnerabilities Found: {sum(len(t.vulnerabilities) for t in self.framework.targets.values())}\n" +
            f"Targets Compromised: {sum(1 for t in self.framework.targets.values() if t.exploited)}\n" +
            f"Operations Executed: {len(self.operations_log)}",
            title="[bold red]🎉 MISSION COMPLETE[/]",
            border_style="green"
        ))
    
    def _extract_commands_from_ai(self, ai_response: str) -> List[str]:
        """Extract executable commands from AI response"""
        commands = []
        
        # Look for code blocks
        code_blocks = re.findall(r'```(?:bash|sh|zsh|shell)?\n([^`]+)```', ai_response, re.IGNORECASE | re.MULTILINE)
        for block in code_blocks:
            for line in block.strip().split('\n'):
                line = line.strip()
                if line and not line.startswith('#') and not line.startswith('//'):
                    commands.append(line)
        
        # Look for specific tool commands
        tool_patterns = [
            r'(nmap [^\\n]+)',
            r'(nikto [^\\n]+)',
            r'(gobuster [^\\n]+)',
            r'(sqlmap [^\\n]+)',
            r'(hydra [^\\n]+)',
            r'(amass [^\\n]+)',
            r'(subfinder [^\\n]+)',
            r'(fierce [^\\n]+)',
            r'(dnsrecon [^\\n]+)',
            r'(enum4linux [^\\n]+)'
        ]
        
        for pattern in tool_patterns:
            matches = re.findall(pattern, ai_response, re.IGNORECASE)
            commands.extend(matches)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_commands = []
        for cmd in commands:
            if cmd not in seen:
                seen.add(cmd)
                unique_commands.append(cmd)
        
        return unique_commands[:10]  # Limit to 10 commands
    
    def _extract_exploit_commands(self, ai_response: str) -> List[str]:
        """Extract Metasploit and exploit commands from AI response"""
        exploit_commands = []
        
        # Metasploit patterns
        msf_patterns = [
            r'(use [^\\n]+)',
            r'(set [^\\n]+)',
            r'(exploit[^\\n]*)',
            r'(msfconsole [^\\n]+)',
            r'(msfvenom [^\\n]+)'
        ]
        
        for pattern in msf_patterns:
            matches = re.findall(pattern, ai_response, re.IGNORECASE)
            exploit_commands.extend(matches)
        
        # Other exploit tools
        exploit_patterns = [
            r'(hydra [^\\n]+)',
            r'(john [^\\n]+)',
            r'(hashcat [^\\n]+)',
            r'(sqlmap [^\\n]+.*--dump)',
            r'(ssh [^\\n]+)',
            r'(telnet [^\\n]+)'
        ]
        
        for pattern in exploit_patterns:
            matches = re.findall(pattern, ai_response, re.IGNORECASE)
            exploit_commands.extend(matches)
        
        return exploit_commands[:5]  # Limit exploit attempts
    
    async def _execute_tool_autonomously(self, command: str, phase: str, target: str = None):
        """Execute tool command autonomously with logging"""
        start_time = time.time()
        
        try:
            # Enhanced command execution with better error handling
            result = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                self._run_command_safely,
                command
            )
            
            duration = time.time() - start_time
            
            # Log operation
            self.operations_log.append({
                'phase': phase,
                'command': command,
                'target': target,
                'timestamp': time.time(),
                'duration': duration,
                'success': result['success'],
                'output_length': len(result['output']),
                'error': result.get('error')
            })
            
            if result['success']:
                self.console.print(f"[green]✅ {phase}: {command[:50]}... ({duration:.1f}s)[/]")
                
                # Save output to file
                if result['output']:
                    output_file = self.framework.results_dir / f"{phase.lower()}_{int(time.time())}.txt"
                    with open(output_file, 'w') as f:
                        f.write(f"Command: {command}\n\n{result['output']}")
            else:
                self.console.print(f"[red]❌ {phase}: {command[:50]}... failed[/]")
                
        except Exception as e:
            self.console.print(f"[red]💥 {phase}: Critical error - {e}[/]")
    
    async def _execute_exploit_autonomously(self, command: str, target: str):
        """Execute exploitation command with extra safety"""
        # Add safety checks for exploitation
        if any(dangerous in command.lower() for dangerous in ['rm -rf', 'format', 'delete', 'destroy']):
            self.console.print(f"[red]🛑 Dangerous command blocked: {command}[/]")
            return
        
        self.console.print(f"[yellow]⚡ Attempting exploitation: {command[:60]}...[/]")
        
        try:
            result = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                self._run_exploit_safely,
                command,
                target
            )
            
            if result['success']:
                # Check if exploitation was successful
                if any(success_indicator in result['output'].lower() for success_indicator in 
                       ['session opened', 'shell', 'meterpreter', 'command shell', 'success']):
                    self.framework.targets[target].exploited = True
                    self.framework.targets[target].shells.append(f"Shell via: {command}")
                    self.console.print(f"[bold green]🎯 EXPLOITATION SUCCESS: {target}[/]")
                else:
                    self.console.print(f"[yellow]⚠️ Exploit attempted but no clear success indicator[/]")
            
            # Log exploit attempt
            self.operations_log.append({
                'phase': 'EXPLOITATION',
                'command': command,
                'target': target,
                'timestamp': time.time(),
                'success': result['success'],
                'exploited': self.framework.targets[target].exploited
            })
            
        except Exception as e:
            self.console.print(f"[red]💥 Exploit execution failed: {e}[/]")
    
    def _run_command_safely(self, command: str) -> Dict[str, Any]:
        """Safely execute command with timeout and error handling"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                cwd=str(self.framework.results_dir)
            )
            
            return {
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr,
                'return_code': result.returncode
            }
        except subprocess.TimeoutExpired:
            return {'success': False, 'error': 'Command timed out', 'output': ''}
        except Exception as e:
            return {'success': False, 'error': str(e), 'output': ''}
    
    def _run_exploit_safely(self, command: str, target: str) -> Dict[str, Any]:
        """Safely execute exploit with additional monitoring"""
        # For Metasploit commands, use msfconsole resource files
        if command.startswith('use ') or 'metasploit' in command.lower():
            return self._run_metasploit_command(command, target)
        else:
            return self._run_command_safely(command)
    
    def _run_metasploit_command(self, command: str, target: str) -> Dict[str, Any]:
        """Execute Metasploit command via resource file"""
        try:
            # Create Metasploit resource file
            resource_file = self.framework.results_dir / f"msf_resource_{int(time.time())}.rc"
            
            with open(resource_file, 'w') as f:
                f.write(f"{command}\n")
                if 'use ' in command:
                    f.write(f"set RHOSTS {target}\n")
                    f.write("set LHOST 0.0.0.0\n")  # Set to appropriate interface
                    f.write("check\n")
                    f.write("exploit -j\n")  # Run as job
                f.write("exit\n")
            
            # Execute via msfconsole
            result = subprocess.run(
                ['msfconsole', '-r', str(resource_file), '-q'],
                capture_output=True,
                text=True,
                timeout=600,  # 10 minute timeout for exploits
                cwd=str(self.framework.results_dir)
            )
            
            return {
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr,
                'return_code': result.returncode
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e), 'output': ''}
    
    async def _ai_analyze_phase_results(self, phase: str):
        """AI analyzes phase results and updates strategy"""
        phase_logs = [log for log in self.operations_log if log['phase'] == phase]
        
        if not phase_logs:
            return
        
        analysis_prompt = f"""
        Phase: {phase}
        Operations completed: {len(phase_logs)}
        Successful operations: {sum(1 for log in phase_logs if log.get('success', False))}
        
        Current targets: {list(self.framework.targets.keys())}
        Current vulnerabilities: {sum(len(t.vulnerabilities) for t in self.framework.targets.values())}
        
        Analyze the results and recommend next steps for the following phase.
        """
        
        analysis = self.framework.query_ollama(
            analysis_prompt,
            f"You are analyzing {phase} results. Provide insights and strategy adjustments for the next phase."
        )
        
        # Store analysis for reporting
        self.operations_log.append({
            'phase': f"{phase}_ANALYSIS",
            'timestamp': time.time(),
            'ai_analysis': analysis,
            'operations_analyzed': len(phase_logs)
        })
        
        self.console.print(Panel(
            Text(analysis[:300] + "..." if len(analysis) > 300 else analysis, style="blue"),
            title=f"[bold blue]🤖 AI {phase} Analysis[/]",
            border_style="blue"
        ))
    
    def _create_status_panel(self, title: str, description: str) -> Panel:
        """Create animated status panel"""
        return Panel(
            Align.center(Text(description, style="cyan")),
            title=f"[bold red]{title}[/]",
            border_style="red"
        )
    
    def get_operations_summary(self) -> Dict[str, Any]:
        """Get summary of all autonomous operations"""
        return {
            'total_operations': len(self.operations_log),
            'successful_operations': sum(1 for log in self.operations_log if log.get('success', False)),
            'phases_completed': list(set(log['phase'] for log in self.operations_log)),
            'targets_identified': len(self.framework.targets),
            'targets_compromised': sum(1 for t in self.framework.targets.values() if t.exploited),
            'total_vulnerabilities': sum(len(t.vulnerabilities) for t in self.framework.targets.values()),
            'operation_log': self.operations_log
        }
