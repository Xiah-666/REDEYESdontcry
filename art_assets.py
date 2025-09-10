#!/usr/bin/env python3
"""Creepy, high-detail ASCII art themes for REDEYESdontcry.
Every major screen picks a different theme. Colors are applied by the caller (pink/red palette).
"""
import os
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.align import Align

console = Console()

_THEMES = {
    "main": r"""
██████╗ ███████╗██████╗ ███████╗██╗   ██╗███████╗███████╗
██╔══██╗██╔════╝██╔══██╗██╔════╝╚██╗ ██╔╝██╔════╝██╔════╝
██████╔╝█████╗  ██║  ██║█████╗   ╚████╔╝ █████╗  ███████╗
██╔══██╗██╔══╝  ██║  ██║██╔══╝    ╚██╔╝  ██╔══╝  ╚════██║
██║  ██║███████╗██████╔╝███████╗   ██║   ███████╗███████║
╚═╝  ╚═╝╚══════╝╚═════╝ ╚══════╝   ╚═╝   ╚══════╝╚══════╝
                         dontcry

    ⣿⡇⣿⡇⣿⡇⣿⡇⣿⡇⣿⡇⣿⡇⣿⡇⣿⡇⣿⡇
    ⣿⡇⣿⣧⣤⣤⣤⣤⣤⣤⣤⣧⣿⡇⣿⡇⣿⡇⣿⡇
    ⣿⡇⣿⡇⠈⠉⠉⠉⠉⠉⠉⠉ ⣿⡇⣿⡇⣿⡇⣿⡇
    ⣿⡇⣿⡇  ̷g̷l̷i̷t̷c̷h̷e̷d̷   ⣿⡇⣿⡇⣿⡇⣿⡇
    ⣿⡇⣿⡇  r̵e̵d̵ e̵y̵e̵s̵   ⣿⡇⣿⡇⣿⡇⣿⡇
""",
    "osint": r"""
   ___  ____  ___ _   _ _____
  / _ \|  _ \|_ _| \ | |_   _|
 | | | | |_) || ||  \| | | |   
 | |_| |  _ < | || |\  | | |   
  \___/|_| \_\___|_| \_| |_|

   ┌─ probing whispers
   ├─ specters in DNS
   ├─ fragments in archives
   └─ footprints in the static
""",
    "enum": r"""
  ███████╗███╗   ██╗██╗   ██╗███╗   ███╗
  ██╔════╝████╗  ██║██║   ██║████╗ ████║
  █████╗  ██╔██╗ ██║██║   ██║██╔████╔██║
  ██╔══╝  ██║╚██╗██║██║   ██║██║╚██╔╝██║
  ███████╗██║ ╚████║╚██████╔╝██║ ╚═╝ ██║
  ╚══════╝╚═╝  ╚═══╝ ╚═════╝ ╚═╝     ╚═╝

  ports breathe. banners lie. wires hum.
""",
    "vuln": r"""
 __     __      _         _ _           _            
 \ \   / /__ _ (_)__ _   | (_)_ _  __ _| |___ _ _ ___
  \ \ / / _ \ '_/ _` |  | | | ' \/ _` | / -_) '_(_-<
   \_/\_/\___/_| \__,_|  |_|_|_||_\__, |_|\___|_| /__/
                                  |___/               

  weak seams. stale versions. soft targets.
""",
    "exploit": r"""
  _____            _       _ _ _   
 | ____|_  ___ __ | | ___ (_) | |_ 
 |  _| \ \/ / '_ \| |/ _ \| | | __|
 | |___ >  <| |_) | | (_) | | | |_ 
 |_____/_/\_\ .__/|_|\___/|_|_|\__|
            |_|                    

  the hinge screams open.
""",
    "post": r"""
  ____           _     _            _ _   _            
 |  _ \ ___  ___| |__ | | ___  __ _| | |_(_) ___  _ __ 
 | |_) / _ \/ __| '_ \| |/ _ \/ _` | | __| |/ _ \| '_ \
 |  __/ (_) \__ \ | | | |  __/ (_| | | |_| | (_) | | | |
 |_|   \___/|___/_| |_|_|\___|\__, |_|\__|_|\___/|_| |_|
                               |___/                     

  persistence. privilege. propagation.
""",
    "chat": r"""
   ___ _           _   
  / __| |_  ___ __| |_ 
 | (__| ' \/ -_) _|  _|
  \___|_||_\___\__|\__|

  whisper to the machine.
""",
    "agent": r"""
    _          _           _                       _   
   /_\  _ _ __| |_ ___  __| |_ _ _ _  _ _ _  __ _ | |  
  / _ \| '_/ _`  _/ _ \/ _` | '_| ' \| '_| |/ _` || |  
 /_/ \_\_| \__,_\__\___/\__,_|_| |_||_|_| |_|\__,_||_|  

  the eyes open without you.
""",
    "report": r"""
  ____                        _ _   
 |  _ \ ___  _ __   ___  _ __(_) |_ 
 | |_) / _ \| '_ \ / _ \| '__| | __|
 |  _ < (_) | |_) | (_) | |  | | |_ 
 |_| \_\___/| .__/ \___/|_|  |_|\__|
            |_|                      

  findings. evidence. consequence.
""",
    "tools": r"""
  _______          _      _____ _           
 |__   __|        | |    / ____| |          
    | |_ __   ___ | | __| (___ | |_ ___  ___
    | | '_ \ / _ \| |/ / \___ \| __/ _ \/ __|
    | | | | | (_) |   <  ____) | ||  __/\__ \
    |_|_| |_|\___/|_|\_\|_____/ \__\___||___/

  blades, each with a story.
""",
}


def print_theme(theme: str) -> None:
    if os.getenv("REDEYES_NO_ART") == "1":
        return
    art = _THEMES.get(theme, _THEMES["main"]).rstrip("\n")
    panel = Panel(Align.center(Text(art, style="red dim")), border_style="red", padding=(0, 2))
    console.print(panel)

