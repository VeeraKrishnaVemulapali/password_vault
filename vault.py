"""
vault.py
--------
Main entry point for the Offline Password Vault CLI.
Run:  python vault.py
"""

import sys
from cryptography.fernet import InvalidToken

import vault_crypto  as crypto
import vault_storage as storage
import vault_utils   as utils
import vault_ui      as ui


# ──────────────────────────────────────────────────────────────────────────────
# Session state
# ──────────────────────────────────────────────────────────────────────────────

_fernet = None          # set after successful login
_master_password = ""   # kept in memory only, never written to disk

MAX_LOGIN_ATTEMPTS = 3


# ──────────────────────────────────────────────────────────────────────────────
# Setup  (first run)
# ──────────────────────────────────────────────────────────────────────────────

def setup_vault() -> bool:
    """Guide the user through creating a brand-new vault."""
    ui.print_banner()
    ui.section_title("🆕  Welcome!  Let's create your vault.")

    print(ui.clr(
        "\n  No vault found. You'll set a Master Password to protect all your entries.",
        ui.C.WHITE
    ))
    print(ui.clr(
        "  ⚠️   Remember this password — it CANNOT be recovered if lost!\n",
        ui.C.YELLOW
    ))

    while True:
        pw1 = ui.prompt_password("Choose a Master Password")
        if len(pw1) < 8:
            ui.print_error("Password must be at least 8 characters.")
            continue
        pw2 = ui.prompt_password("Confirm Master Password")
        if pw1 != pw2:
            ui.print_error("Passwords do not match. Try again.")
            continue
        break

    salt        = crypto.generate_salt()
    master_hash = crypto.hash_master_password(pw1, salt)
    storage.create_vault(salt, master_hash)

    global _fernet, _master_password
    _fernet         = crypto.get_fernet(pw1, salt)
    _master_password = pw1

    ui.print_success("Vault created successfully!  Welcome to PassVault.")
    ui.pause()
    return True


# ──────────────────────────────────────────────────────────────────────────────
# Login
# ──────────────────────────────────────────────────────────────────────────────

def login() -> bool:
    """Authenticate with the master password.  Returns True on success."""
    meta = storage.load_meta()

    for attempt in range(1, MAX_LOGIN_ATTEMPTS + 1):
        ui.print_banner()
        ui.section_title("🔐  Unlock Your Vault")

        if attempt > 1:
            ui.print_warning(f"Attempt {attempt}/{MAX_LOGIN_ATTEMPTS}")

        pw = ui.prompt_password("Master Password")

        if crypto.verify_master_password(pw, meta["salt"], meta["master_hash"]):
            global _fernet, _master_password
            _fernet          = crypto.get_fernet(pw, meta["salt"])
            _master_password = pw
            ui.print_success("Vault unlocked successfully!")
            ui.pause()
            return True
        else:
            ui.print_error("Incorrect master password.")

    ui.print_error("Too many failed attempts. Vault locked.")
    return False


# ──────────────────────────────────────────────────────────────────────────────
# Actions
# ──────────────────────────────────────────────────────────────────────────────

def action_add() -> None:
    """Add a new password entry to the vault."""
    ui.section_title("➕  Add New Entry")

    website  = ui.prompt("Website / Service name")
    if not website:
        ui.print_error("Website cannot be empty.")
        return

    username = ui.prompt("Username / Email")
    notes    = ui.prompt("Notes (optional)")

    # Allow user to type their own password or generate one
    use_gen = ui.confirm("Generate a secure password automatically?")
    if use_gen:
        length   = ui.prompt_int("Password length", 8, 128) or 16
        password = utils.generate_password(length)
        print(ui.clr(f"\n  Generated: {password}", ui.C.YELLOW, ui.C.BOLD))
    else:
        while True:
            password = ui.prompt_password("Password")
            if not password:
                ui.print_error("Password cannot be empty.")
                continue
            rating, tips = utils.check_strength(password)
            colour = ui.C.RED if rating in ("Weak", "Fair") else ui.C.GREEN
            print(ui.clr(f"\n  Strength: {rating}", colour, ui.C.BOLD))
            if tips:
                for tip in tips:
                    print(ui.clr(f"   • {tip}", ui.C.DIM))
            if rating == "Weak" and not ui.confirm("Password is weak. Use it anyway?"):
                continue
            break

    encrypted = crypto.encrypt_password(password, _fernet)
    entry = {
        "website":  website,
        "username": username,
        "password": encrypted,
        "notes":    notes,
    }
    storage.add_entry(entry)
    ui.print_success(f'Entry for "{website}" saved!')

    if ui.confirm("Copy password to clipboard?"):
        if utils.copy_to_clipboard(password):
            ui.print_info("Copied to clipboard!")
        else:
            ui.print_warning("pyperclip not available. Install it with: pip install pyperclip")

    ui.pause()


def action_search() -> None:
    """Search for and display matching entries."""
    ui.section_title("🔍  Search Entries")

    keyword = ui.prompt("Enter website / service keyword")
    if not keyword:
        ui.print_error("Search term cannot be empty.")
        ui.pause()
        return

    matches = storage.find_entries(keyword)
    if not matches:
        ui.print_warning(f'No entries found for "{keyword}".')
        ui.pause()
        return

    print(ui.clr(f"\n  Found {len(matches)} result(s):", ui.C.CYAN))

    # Decrypt passwords for display
    decrypted = []
    for e in matches:
        try:
            plain = crypto.decrypt_password(e["password"], _fernet)
            decrypted.append({**e, "plain": plain})
        except InvalidToken:
            decrypted.append({**e, "plain": "⚠️ Decryption failed"})

    ui.display_entries(decrypted, show_password=False)

    if len(decrypted) == 1 or ui.confirm("Reveal password(s)?"):
        for i, e in enumerate(decrypted):
            ui.display_entry(e, index=i, show_password=True)
            if utils.clipboard_available():
                if ui.confirm(f"Copy password for [{e['website']}] to clipboard?"):
                    utils.copy_to_clipboard(e["plain"])
                    ui.print_info("Copied!")

    ui.pause()


def action_list_all() -> None:
    """List all vault entries (passwords hidden)."""
    ui.section_title("📋  All Entries")

    entries = storage.load_entries()
    if not entries:
        ui.print_warning("Your vault is empty. Add your first entry!")
        ui.pause()
        return

    print(ui.clr(f"\n  Total entries: {len(entries)}", ui.C.CYAN))
    for i, e in enumerate(entries):
        ui.display_entry(e, index=i, show_password=False)

    ui.pause()


def action_edit() -> None:
    """Edit an existing entry."""
    ui.section_title("✏️  Edit Entry")

    entries = storage.load_entries()
    if not entries:
        ui.print_warning("Vault is empty.")
        ui.pause()
        return

    for i, e in enumerate(entries):
        ui.display_entry(e, index=i)

    idx = ui.prompt_int("Enter entry number to edit", 0, len(entries) - 1)
    if idx is None:
        return

    entry = entries[idx]

    print(ui.clr("\n  Leave blank to keep the current value.", ui.C.DIM))
    new_website  = ui.prompt(f"Website [{entry['website']}]") or entry["website"]
    new_username = ui.prompt(f"Username [{entry['username']}]") or entry["username"]
    new_notes    = ui.prompt(f"Notes [{entry.get('notes','')}]") or entry.get("notes", "")

    change_pw = ui.confirm("Change the password?")
    if change_pw:
        use_gen = ui.confirm("Generate a new password?")
        if use_gen:
            length      = ui.prompt_int("Password length", 8, 128) or 16
            new_plain   = utils.generate_password(length)
            print(ui.clr(f"\n  Generated: {new_plain}", ui.C.YELLOW, ui.C.BOLD))
        else:
            new_plain = ui.prompt_password("New password")
        new_enc = crypto.encrypt_password(new_plain, _fernet)
    else:
        new_enc = entry["password"]

    updated = {
        "website":  new_website,
        "username": new_username,
        "password": new_enc,
        "notes":    new_notes,
    }

    if storage.update_entry(idx, updated):
        ui.print_success("Entry updated successfully!")
    else:
        ui.print_error("Update failed (invalid index).")

    ui.pause()


def action_delete() -> None:
    """Delete an entry from the vault."""
    ui.section_title("🗑️  Delete Entry")

    entries = storage.load_entries()
    if not entries:
        ui.print_warning("Vault is empty.")
        ui.pause()
        return

    for i, e in enumerate(entries):
        ui.display_entry(e, index=i)

    idx = ui.prompt_int("Enter entry number to delete", 0, len(entries) - 1)
    if idx is None:
        return

    target = entries[idx]
    if ui.confirm(f'Permanently delete entry for "{target["website"]}"?'):
        if storage.delete_entry(idx):
            ui.print_success(f'Entry for "{target["website"]}" deleted.')
        else:
            ui.print_error("Deletion failed.")
    else:
        ui.print_info("Deletion cancelled.")

    ui.pause()


def action_generate() -> None:
    """Generate a standalone password (not saved)."""
    ui.section_title("⚡  Password Generator")

    print(ui.clr("\n  Choose generator type:", ui.C.WHITE))
    print(f"  {ui.clr('1', ui.C.CYAN, ui.C.BOLD)}  Random (symbols + numbers)")
    print(f"  {ui.clr('2', ui.C.CYAN, ui.C.BOLD)}  Memorable passphrase")

    choice = ui.prompt("Type", "1")

    if choice == "2":
        words    = ui.prompt_int("Number of words", 2, 8) or 4
        password = utils.generate_memorable_password(words)
    else:
        length   = ui.prompt_int("Password length", 8, 128) or 16
        password = utils.generate_password(length)

    rating, tips = utils.check_strength(password)
    colour = ui.C.RED if rating in ("Weak",) else ui.C.GREEN

    print(ui.clr(f"\n  ✨  Generated Password:", ui.C.MAGENTA, ui.C.BOLD))
    print(ui.clr(f"      {password}", ui.C.YELLOW, ui.C.BOLD))
    print(ui.clr(f"  💪  Strength : {rating}", colour))

    if ui.confirm("Copy to clipboard?"):
        if utils.copy_to_clipboard(password):
            ui.print_info("Password copied to clipboard!")
        else:
            ui.print_warning("pyperclip not installed. Run: pip install pyperclip")

    ui.pause()


def action_check_strength() -> None:
    """Check the strength of any password the user types."""
    ui.section_title("💪  Password Strength Checker")

    password = ui.prompt_password("Enter password to check")
    if not password:
        ui.print_error("No password entered.")
        ui.pause()
        return

    rating, tips = utils.check_strength(password)

    colour_map = {
        "Weak":        ui.C.RED,
        "Fair":        ui.C.YELLOW,
        "Strong":      ui.C.GREEN,
        "Very Strong": ui.C.CYAN,
    }
    colour = colour_map.get(rating, ui.C.WHITE)

    bar_len = {"Weak": 2, "Fair": 4, "Strong": 6, "Very Strong": 8}
    filled  = bar_len.get(rating, 0)
    bar     = "█" * filled + "░" * (8 - filled)

    print()
    print(ui.clr(f"  Strength : {rating}", colour, ui.C.BOLD))
    print(ui.clr(f"  [{bar}]", colour))

    if tips:
        print(ui.clr("\n  Suggestions:", ui.C.DIM))
        for tip in tips:
            print(ui.clr(f"   • {tip}", ui.C.DIM))
    else:
        print(ui.clr("\n  🎉 Your password is excellent!", ui.C.GREEN))

    ui.pause()


# ──────────────────────────────────────────────────────────────────────────────
# Main loop
# ──────────────────────────────────────────────────────────────────────────────

ACTION_MAP = {
    "1": action_add,
    "2": action_search,
    "3": action_list_all,
    "4": action_edit,
    "5": action_delete,
    "6": action_generate,
    "7": action_check_strength,
}


def main() -> None:
    # ── Bootstrap ──────────────────────────────────────────────────────────────
    ui.print_splash_screen()
    if not storage.vault_exists():
        ok = setup_vault()
    else:
        ok = login()

    if not ok:
        sys.exit(1)

    # ── Main menu loop ─────────────────────────────────────────────────────────
    while True:
        ui.print_main_menu()
        choice = input(ui.clr("  ▶  Your choice: ", ui.C.WHITE, ui.C.BOLD)).strip()

        if choice == "8":
            ui.print_banner()
            print(ui.clr("  🔒  Vault locked. Stay safe!\n", ui.C.CYAN, ui.C.BOLD))
            sys.exit(0)

        handler = ACTION_MAP.get(choice)
        if handler:
            handler()
        else:
            ui.print_error(f'Unknown option "{choice}". Please choose 1-8.')
            ui.pause()


# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    main()
