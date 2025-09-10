#!/usr/bin/env python3
import os
import argparse
from rich.console import Console

console = Console()

def main():
    """CLI wrapper with basic flags and preflight check.
    """
    parser = argparse.ArgumentParser(prog="redeyes", description="REDEYESdontcry - Red Team TUI with AI")
    parser.add_argument("--check", action="store_true", help="Run environment/tool preflight and exit")
    parser.add_argument("--no-art", action="store_true", help="Disable ASCII art rendering")
    parser.add_argument("--assume-yes", "-y", action="store_true", help="Assume yes for any notices")
    parser.add_argument("--results-dir", type=str, default=None, help="Override results directory")
    parser.add_argument("--model", type=str, default=None, help="Preferred Ollama model name")
    parser.add_argument("--log-level", type=str, default=None, help="Log level (INFO/DEBUG/WARN/ERROR)")
    parser.add_argument("--intensity", type=int, default=None, help="Art intensity 0..2")
    args = parser.parse_args()

    # Apply environment flags
    if args.no_art:
        os.environ["REDEYES_NO_ART"] = "1"
    if args.assume_yes:
        os.environ["REDEYES_ASSUME_YES"] = "1"
    if args.results_dir:
        os.environ["REDEYES_RESULTS_DIR"] = args.results_dir
    if args.model:
        os.environ["REDEYES_MODEL"] = args.model
    if args.log_level:
        os.environ["REDEYES_LOG_LEVEL"] = args.log_level
    if args.intensity is not None:
        os.environ["REDEYES_ART_INTENSITY"] = str(args.intensity)

    try:
        from REDEYESdontcry import REDEYESFramework
    except Exception as e:
        console.print("[bright_red]Failed to import legacy framework (REDEYESdontcry.py).\n"
                       "Run this command from the project root, or run ./REDEYESdontcry.py directly.[/]")
        console.print(f"[red]Import error:[/] {e}\n")
        raise SystemExit(1)

    try:
        app = REDEYESFramework()
        if args.check:
            # Show tool and environment status then exit
            app.show_tool_status()
            return
        app.show_main_menu()
    except KeyboardInterrupt:
        console.print("\n[red]Exiting...[/]")
    except Exception as e:
        console.print(f"[bright_red]Unhandled error:[/] {e}")
        raise

