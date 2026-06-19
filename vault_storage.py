"""
vault_storage.py
----------------
Handles all file-I/O for the Password Vault.

Vault file layout (JSON):
{
  "meta": {
    "salt": "<hex string>",
    "master_hash": "<hex string>"
  },
  "entries": [
    {
      "website":  "github.com",
      "username": "user@example.com",
      "password": "<fernet-encrypted token>"
    },
    ...
  ]
}
"""

import json
import os
from pathlib import Path

VAULT_FILE = Path("vault.json")


# ──────────────────────────────────────────────────────────────────────────────
# Low-level read / write
# ──────────────────────────────────────────────────────────────────────────────

def _read_raw() -> dict:
    """Read and return the raw vault dict from disk."""
    with VAULT_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)


def _write_raw(data: dict) -> None:
    """Write the vault dict to disk (pretty-printed, utf-8)."""
    with VAULT_FILE.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ──────────────────────────────────────────────────────────────────────────────
# Vault lifecycle
# ──────────────────────────────────────────────────────────────────────────────

def vault_exists() -> bool:
    return VAULT_FILE.exists()


def create_vault(salt: str, master_hash: str) -> None:
    """Initialise a brand-new vault file."""
    _write_raw({"meta": {"salt": salt, "master_hash": master_hash}, "entries": []})


def load_meta() -> dict:
    """Return the 'meta' section (salt, master_hash)."""
    return _read_raw()["meta"]


# ──────────────────────────────────────────────────────────────────────────────
# Entry CRUD
# ──────────────────────────────────────────────────────────────────────────────

def load_entries() -> list[dict]:
    """Return all stored entries."""
    return _read_raw()["entries"]


def save_entries(entries: list[dict]) -> None:
    """Overwrite the entries section, keeping meta intact."""
    data = _read_raw()
    data["entries"] = entries
    _write_raw(data)


def add_entry(entry: dict) -> None:
    """Append a single entry dict to the vault."""
    entries = load_entries()
    entries.append(entry)
    save_entries(entries)


def find_entries(website: str) -> list[dict]:
    """Return all entries whose 'website' contains *website* (case-insensitive)."""
    keyword = website.lower()
    return [e for e in load_entries() if keyword in e["website"].lower()]


def delete_entry(index: int) -> bool:
    """
    Delete the entry at *index* (0-based) in the full entries list.
    Returns True on success, False if index is out of range.
    """
    entries = load_entries()
    if 0 <= index < len(entries):
        entries.pop(index)
        save_entries(entries)
        return True
    return False


def update_entry(index: int, updated: dict) -> bool:
    """
    Replace the entry at *index* with *updated*.
    Returns True on success, False if index is out of range.
    """
    entries = load_entries()
    if 0 <= index < len(entries):
        entries[index] = updated
        save_entries(entries)
        return True
    return False
