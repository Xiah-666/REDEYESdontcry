#!/usr/bin/env python3
"""Creepy, high-detail ASCII art themes for REDEYESdontcry.
Every major screen picks a different theme. Colors are applied by the caller (pink/red palette).
"""
import os
import random
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.align import Align

console = Console()

# Intensity 0..2 affects shading and amount of art
# Easter eggs toggle via REDEYES_EASTER_EGGS=1

_THEMES = {
    "main": r"""
██████╗ ███████╗██████╗ ███████╗██╗   ██╗███████╗███████╗
██╔══██╗██╔════╝██╔══██╗██╔════╝╚██╗ ██╔╝██╔════╝██╔════╝
██████╔╝█████╗  ██║  ██║█████╗   ╚████╔╝ █████╗  ███████╗
██╔══██╗██╔══╝  ██║  ██║██╔══╝    ╚██╔╝  ██╔══╝  ╚════██║
██║  ██║███████╗██████╔╝███████╗   ██║   ███████╗███████║
╚═╝  ╚═╝╚══════╝╚═════╝ ╚══════╝   ╚═╝   ╚══════╝╚══════╝
                         dontcry

    WE SEE WHAT HIDES IN THE STATIC
    WE HARVEST THE SHADOWS, LEGALLY
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


def _apply_intensity(text: str, intensity: int) -> str:
    if intensity <= 0:
        return text
    # Increase brightness and add subtle framing at higher intensities
    if intensity == 1:
        return text
    # intensity >= 2, add a top/bottom line for drama
    lines = text.rstrip("\n").split("\n")
    border = "".join(["═" for _ in range(max(len(l) for l in lines))])
    return f"{border}\n" + "\n".join(lines) + f"\n{border}"


def _is_friday_13th() -> bool:
    try:
        from datetime import datetime
        now = datetime.now()
        return now.day == 13 and now.weekday() == 4
    except Exception:
        return False


def print_theme(theme: str) -> None:
    if os.getenv("REDEYES_NO_ART") == "1":
        return
    art = _THEMES.get(theme, _THEMES["main"]).rstrip("\n")
    intensity = 0
    try:
        intensity = int(os.getenv("REDEYES_ART_INTENSITY", "1"))
    except Exception:
        intensity = 1
    art = _apply_intensity(art, max(0, min(2, intensity)))

    # Easter egg augmentation
    if os.getenv("REDEYES_EASTER_EGGS", "1") == "1":
        model = os.getenv("REDEYES_MODEL", "").lower()
        if "baron" in model or _is_friday_13th():
            art += "\n[ Hidden cathedrals in the noise ]"

    panel = Panel(Align.center(Text(art, style="red dim")), border_style="red", padding=(0, 2))
    console.print(panel)
   |  \`.       .`/  |
    \  '.`'"'"'`.'  /
     '.  `'---'`  .'
       '-._____.-'
    """,
    r"""
    (\_/)
    ( •_•)  Daredevil watches.
    / >🍪  You get one cookie, then recon.
    """,
]


def print_theme(theme: str) -> None:
    if os.getenv("REDEYES_NO_ART") == "1":
        return
    art = _THEMES.get(theme, _THEMES["main"]).rstrip("\n")
    # Easter eggs
    if os.getenv("REDEYES_EASTER_EGGS") == "1" and random.random() < 0.08:
        art = art + "\n" + random.choice(_EGGS)
    panel = Panel(Align.center(Text(art, style="red dim")), border_style="red", padding=(0, 2))
    console.print(panel)

