#!/usr/bin/env python3
from rich.console import Console

console = Console()

def main():
    """Thin CLI wrapper that launches the TUI framework.
    For now, it imports the legacy main module to preserve functionality.
    """
    try:
        from REDEYESdontcry import REDEYESFramework
    except Exception as e:
        console.print("[bright_red]Failed to import legacy framework (REDEYESdontcry.py).\n"
                       "Run this command from the project root, or run ./REDEYESdontcry.py directly.[/]")
        console.print(f"[red]Import error:[/] {e}
")
        raise SystemExit(1)

    try:
        app = REDEYESFramework()
        app.show_main_menu()
    except KeyboardInterrupt:
        console.print("\n[red]Exiting...[/]")
    except Exception as e:
        console.print(f"[bright_red]Unhandled error:[/] {e}")
        raise

