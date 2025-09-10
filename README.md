# 👁️ REDEYESdontcry

**Advanced Red Team TUI Framework with AI Integration**

A professional penetration testing suite designed for Kali Linux / Tsurugi Linux with beautiful terminal UI, context-aware AI assistance, and comprehensive tool automation.

## ✨ Features

### 🎨 Beautiful Terminal UI
- Rich TUI interface with comprehensive menus
- **Pink text for user input, red for AI/agent responses** 
- Professional ASCII art with disturbed aesthetics
- Real-time status indicators and progress bars
- Emoji-enhanced user experience

### 🤖 AI Integration
- **Auto-detects uncensored/abliterated Ollama models**
- Prioritizes models like NeuralDaredevil, Wizard-Vicuna, Dolphin
- Context-aware AI assistant with test data integration
- AI-powered vulnerability analysis and exploitation recommendations
- Chat interface with persistent conversation history

### 🔥 Professional Pentesting Workflow
- **Complete OSINT to exploitation pipeline**
- Automated tool execution with intelligent output parsing
- Session management with comprehensive logging
- Target tracking with vulnerability correlation
- Real-time scan results analysis

### 🛠️ Tool Integration (30+ Tools)
- **Network Scanning**: nmap, masscan, zmap
- **Web Testing**: nikto, gobuster, dirb, sqlmap, wpscan
- **OSINT**: theHarvester, fierce, amass, subfinder, recon-ng
- **Exploitation**: metasploit, hydra, john, hashcat
- **Services**: enum4linux, smbclient, snmp enumeration

## 🚀 Quick Start

### Installation
```bash
# Clone or download the framework files
chmod +x setup.sh
./setup.sh
```

### Launch
```bash
./REDEYESdontcry.py
```

## 📋 Menu Structure

### 1. 🔍 OSINT & Reconnaissance
- 🌐 Domain/IP Information (whois) ✅ **Working**
- 🔍 DNS Reconnaissance ✅ **Working**  
- 📡 Subdomain Enumeration
- 🕷️ The Harvester
- 🌍 Shodan Search
- ⚔️ Fierce DNS Scanner
- 🔧 Custom OSINT Workflow
- 🤖 AI-Powered OSINT Analysis ✅ **Working**

### 2. 🌐 Network Enumeration
- Host Discovery
- Port Scanning (Fast/Full)
- Service Enumeration
- SMB/SNMP Enumeration
- AI Scan Planning

### 3. 🔎 Vulnerability Scanning
- Nmap Vulnerability Scripts
- Nikto Web Scanner
- Directory Brute Force
- SQL Injection Testing
- SSL/TLS Analysis

### 4. 💥 Exploitation
- Metasploit Integration
- Password Attacks
- Hash Cracking
- Web Exploitation
- AI-Guided Exploitation

### 5. 🔓 Post-Exploitation
- Privilege Escalation
- Persistence Mechanisms
- Lateral Movement
- Data Exfiltration

### 6. 📊 Log Analysis
- Log Parsing and Analysis
- Timeline Construction
- IOC Extraction
- Reporting Integration

### 7. 🤖 AI Chat Assistant ✅ **Working**
- Context-aware conversations
- Exploitation strategy recommendations
- Tool usage guidance
- Step-by-step attack planning

### 8. 🎯 Target Management
- Target tracking and organization
- Vulnerability correlation
- Progress monitoring
- Export/Import capabilities

## 🎯 Hardware Optimization

### Optimized for 6GB VRAM + 60GB DDR4
- **Primary AI Model**: NeuralDaredevil-8B-Abliterated (4.7GB)
- **Fallback**: Wizard-Vicuna-7B-Uncensored (3.8GB)
- **Advanced**: Huihui GPT-OSS-20B with layer offloading
- Automatic memory management and model selection

### Performance Tips
```bash
# Enable layer offloading for larger models
ollama run neuraldaredevil-8b-abliterated --gpu-layers 28

# Reduce context for memory efficiency  
ollama run model --ctx-size 4096

# Enable memory mapping
export OLLAMA_MMAP=1
```

## 🤖 AI Model Recommendations

### Best Models for Pentesting

#### 1. **NeuralDaredevil-8B-Abliterated** ⭐ **TOP CHOICE**
```bash
ollama pull closex/neuraldaredevil-8b-abliterated
```
- **Size**: 4.7GB
- **Specialization**: Cybersecurity and exploitation
- **Performance**: Best for tool usage and vulnerability analysis

#### 2. **Wizard-Vicuna-7B-Uncensored**
```bash
ollama pull wizard-vicuna-uncensored:7b
```
- **Size**: 3.8GB  
- **Specialization**: General pentesting guidance
- **Performance**: Fast, resource-efficient

#### 3. **Qwen2.5-Coder-7B-Abliterated** 
```bash
ollama pull qwen2.5-coder:7b
```
- **Size**: 4.5GB
- **Specialization**: Exploit development and scripting
- **Performance**: Excellent for custom tool creation

## 📖 Usage Examples

### Basic OSINT Workflow
1. Launch framework: `./REDEYESdontcry.py`
2. Select "1" for OSINT & Reconnaissance
3. Run whois lookup on target domain
4. Perform DNS reconnaissance
5. Use AI analysis for strategic planning

### AI-Assisted Exploitation
1. Navigate to "7" AI Chat Assistant
2. Ask: "Analyze the vulnerabilities on my current target"
3. Request: "Give me step-by-step exploitation commands"
4. Execute suggested commands with confirmation

### Target Management
1. Select "8" Target Management  
2. Add targets manually or via discovery
3. Track progress across different phases
4. Generate comprehensive reports

## 🔧 Configuration

### Environment Variables
```bash
# Ollama configuration
export OLLAMA_HOST=localhost
export OLLAMA_PORT=11434
export OLLAMA_MMAP=1
export OLLAMA_NUM_THREADS=8

# Framework settings
export REDEYES_RESULTS_DIR=~/redeyes_results
export REDEYES_LOG_LEVEL=INFO
```

### Custom Tool Paths
Edit the framework to add custom tool locations:
```python
tools = {
    'custom_tool': '/path/to/custom/tool',
    'proprietary_scanner': '/opt/scanner/bin/scanner'
}
```

## 📁 Output Structure

```
/tmp/redeyesdontcry_YYYYMMDD_HHMMSS/
├── redeyesdontcry_YYYYMMDD_HHMMSS.log   # Session log
├── whois_target_com.txt                 # OSINT results
├── dnsrecon_target_com.txt              # DNS reconnaissance
├── nmap_192_168_1_100.xml               # Port scan results
├── nikto_192_168_1_100_80.txt           # Web vulnerability scans
├── metasploit_192_168_1_100.txt         # Exploitation attempts
└── ai_chat_history.json                 # AI conversation log
```

## 🛡️ Security & Ethics

### Legal Disclaimer
- **AUTHORIZED TESTING ONLY**: This framework is designed for authorized penetration testing
- **Written Permission Required**: Only use with explicit written authorization
- **Compliance**: Users are responsible for compliance with local laws and regulations
- **Professional Use**: Intended for security professionals and authorized researchers

### Safety Features
- No destructive actions by default
- Confirmation prompts for dangerous operations
- Comprehensive logging for accountability
- Boundary checking and scope limitation

## 🔍 Troubleshooting

### Common Issues

#### Ollama Not Detected
```bash
# Check Ollama service
systemctl status ollama
sudo systemctl restart ollama

# Verify models
ollama list
```

#### Permission Errors
```bash
# Fix script permissions
chmod +x redeyes_complete.py

# Check tool accessibility  
which nmap nikto gobuster
```

#### Memory Issues
```bash
# Monitor memory usage
htop

# Use lighter models
ollama pull wizard-vicuna-uncensored:7b

# Enable model offloading
ollama run model --gpu-layers 15
```

#### Missing Tools
```bash
# Install missing tools
sudo apt update
sudo apt install nmap nikto gobuster metasploit-framework

# Check installation
./REDEYESdontcry.py
# Navigate to "9" Tool Status
```

## 🚧 Development Status

### ✅ Implemented Features
- Beautiful TUI with Rich library
- Ollama AI integration with model auto-detection
- OSINT workflows (whois, DNS reconnaissance)
- AI chat assistant with context awareness
- Comprehensive tool detection (30+ tools)
- Session management and logging
- Professional menu system with emojis

### 🔨 In Development
- Complete network enumeration workflows
- Vulnerability scanning automation
- Metasploit integration and automation
- Web application testing workflows
- Post-exploitation modules
- Log analysis and timeline construction
- Report generation with AI insights

### 🎯 Planned Features
- Distributed scanning capabilities
- Custom exploit development environment
- Integration with external APIs (Shodan, VirusTotal)
- Real-time collaboration features
- Advanced reporting with charts and graphs

## 🤝 Contributing

This framework is designed to be extensible. To contribute:

1. **Tool Integration**: Add new tools to the `detect_tools()` method
2. **Menu Extensions**: Create new menu functions following existing patterns  
3. **AI Prompts**: Improve system prompts for better AI responses
4. **Workflow Automation**: Add custom automation scripts
5. **Output Parsing**: Enhance result parsing and analysis

### Development Guidelines
- Follow the existing TUI design patterns
- Maintain the pink/red color scheme
- Include comprehensive error handling
- Add logging for all operations
- Test with various target environments

## 📞 Support

### Getting Help
- Check the troubleshooting section above
- Review the comprehensive setup script
- Test individual tools manually first
- Verify Ollama model availability

### Reporting Issues
- Include system information (OS, Python version)
- Provide error messages and log excerpts
- Describe steps to reproduce the issue
- Include relevant configuration details

## 📜 License

This framework is provided for educational and authorized security testing purposes only. Users assume all responsibility for legal and ethical compliance.

---

**👁️ With great power comes great responsibility. Use REDEYESdontcry ethically and only with proper authorization. 👁️**

## 🎵 Credits

*"The sickness is rising, the voices are calling..."*

Created with the aesthetics and intensity of Disturbed's "Down with the Sickness" - because sometimes penetration testing requires a little chaos to find order in the security landscape.

**Stay disturbed, stay vigilant. 🔥**