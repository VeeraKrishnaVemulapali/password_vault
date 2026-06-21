"""
vault_ui.py
-----------
All terminal UI helpers: coloured output, banners, menus, and prompts.
No external libraries required — colours use ANSI escape codes.
"""

import os
import sys
import getpass


# ──────────────────────────────────────────────────────────────────────────────
# Enable ANSI colours on Windows
# ──────────────────────────────────────────────────────────────────────────────

if sys.platform == "win32":
    import ctypes
    try:
        kernel32 = ctypes.windll.kernel32          # type: ignore[attr-defined]
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    except Exception:
        pass


# ──────────────────────────────────────────────────────────────────────────────
# ANSI colour codes
# ──────────────────────────────────────────────────────────────────────────────

class C:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"
    RED     = "\033[91m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    BLUE    = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN    = "\033[96m"
    WHITE   = "\033[97m"
    BG_DARK = "\033[40m"


def clr(text: str, *codes: str) -> str:
    return "".join(codes) + text + C.RESET


def clear_screen() -> None:
    os.system("cls" if sys.platform == "win32" else "clear")


# ──────────────────────────────────────────────────────────────────────────────
# Banner
# ──────────────────────────────────────────────────────────────────────────────

BANNER = r"""
  ██████╗  █████╗ ███████╗███████╗    ██╗   ██╗ █████╗ ██╗   ██╗██╗  ████████╗
  ██╔══██╗██╔══██╗██╔════╝██╔════╝    ██║   ██║██╔══██╗██║   ██║██║  ╚══██╔══╝
  ██████╔╝███████║███████╗███████╗    ██║   ██║███████║██║   ██║██║     ██║
  ██╔═══╝ ██╔══██║╚════██║╚════██║    ╚██╗ ██╔╝██╔══██║██║   ██║██║     ██║
  ██║     ██║  ██║███████║███████║     ╚████╔╝ ██║  ██║╚██████╔╝███████╗██║
  ╚═╝     ╚═╝  ╚═╝╚══════╝╚══════╝     ╚═══╝  ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝
"""


def print_banner() -> None:
    clear_screen()
    print(clr(BANNER, C.CYAN, C.BOLD))
    print(clr("  🔐  Offline Password Vault  |  Your secrets, locked & local.\n", C.DIM))


def print_splash_screen() -> None:
    clear_screen()
    print(clr(BANNER, C.CYAN, C.BOLD))
    print(clr("  🔐  Welcome to the Offline Password Vault", C.MAGENTA, C.BOLD))
    print(clr("  =======================================", C.MAGENTA, C.BOLD))
    print(clr("  Your secrets, locked & local. Never stored in the cloud.\n", C.DIM))
    input(clr("  ▶  Press Enter to start your vault session...", C.GREEN, C.BOLD))
    clear_screen()


def print_separator(char: str = "─", width: int = 70, colour: str = C.BLUE) -> None:
    print(clr(char * width, colour))


def print_success(msg: str) -> None:
    print(clr(f"\n  ✅  {msg}", C.GREEN, C.BOLD))


def print_error(msg: str) -> None:
    print(clr(f"\n  ❌  {msg}", C.RED, C.BOLD))


def print_warning(msg: str) -> None:
    print(clr(f"\n  ⚠️   {msg}", C.YELLOW))


def print_info(msg: str) -> None:
    print(clr(f"\n  ℹ️   {msg}", C.CYAN))


def section_title(title: str) -> None:
    print()
    print_separator()
    print(clr(f"  {title}", C.MAGENTA, C.BOLD))
    print_separator()


# ──────────────────────────────────────────────────────────────────────────────
# Prompts
# ──────────────────────────────────────────────────────────────────────────────

def prompt(label: str, default: str = "") -> str:
    """Generic text prompt."""
    suffix = f" [{default}]" if default else ""
    value = input(clr(f"\n  ▶  {label}{suffix}: ", C.WHITE, C.BOLD)).strip()
    return value if value else default


def prompt_password(label: str = "Password") -> str:
    """Hidden password prompt (does not echo input)."""
    return getpass.getpass(clr(f"\n  🔑  {label}: ", C.YELLOW, C.BOLD))


def prompt_int(label: str, min_val: int = 1, max_val: int = 999) -> int | None:
    """Prompt for an integer within [min_val, max_val]. Returns None on blank input."""
    raw = input(clr(f"\n  ▶  {label} ({min_val}-{max_val}): ", C.WHITE, C.BOLD)).strip()
    if not raw:
        return None
    try:
        val = int(raw)
        if min_val <= val <= max_val:
            return val
        print_error(f"Please enter a number between {min_val} and {max_val}.")
    except ValueError:
        print_error("Invalid number.")
    return None


def confirm(question: str) -> bool:
    """Ask a yes/no question; returns True for 'y'."""
    ans = input(clr(f"\n  ▶  {question} (y/n): ", C.YELLOW)).strip().lower()
    return ans == "y"


# ──────────────────────────────────────────────────────────────────────────────
# Menu
# ──────────────────────────────────────────────────────────────────────────────

MAIN_MENU = [
    ("1", "➕  Add a new password entry"),
    ("2", "🔍  Search / retrieve a password"),
    ("3", "📋  List all entries"),
    ("4", "✏️   Edit an existing entry"),
    ("5", "🗑️   Delete an entry"),
    ("6", "⚡  Generate a secure password"),
    ("7", "💪  Check password strength"),
    ("8", "🚪  Lock & exit"),
]


def print_main_menu() -> None:
    print_banner()
    print_separator()
    print(clr("  MAIN MENU", C.MAGENTA, C.BOLD))
    print_separator()
    for key, label in MAIN_MENU:
        print(f"  {clr(key, C.CYAN, C.BOLD)}  {label}")
    print_separator()


# ──────────────────────────────────────────────────────────────────────────────
# Entry display
# ──────────────────────────────────────────────────────────────────────────────

def display_entry(entry: dict, index: int | None = None, show_password: bool = False) -> None:
    """Pretty-print a single vault entry."""
    prefix = f"[{index}] " if index is not None else ""
    print()
    print(clr(f"  {prefix}🌐  Website : {entry['website']}", C.CYAN))
    print(clr(f"       👤  Username: {entry['username']}", C.WHITE))
    if show_password:
        print(clr(f"       🔑  Password: {entry.get('plain', '***')}", C.YELLOW, C.BOLD))
    else:
        print(clr("       🔑  Password: " + "●" * 12, C.DIM))
    if entry.get("notes"):
        print(clr(f"       📝  Notes   : {entry['notes']}", C.DIM))


def display_entries(entries: list[dict], show_password: bool = False) -> None:
    if not entries:
        print_warning("No entries found.")
        return
    for i, e in enumerate(entries):
        display_entry(e, index=i, show_password=show_password)
    print()


def pause() -> None:
    """Wait for the user to press Enter before continuing."""
    input(clr("\n  Press Enter to continue…", C.DIM))
