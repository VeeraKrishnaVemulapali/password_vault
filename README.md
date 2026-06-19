# 🔐 PassVault — Offline Password Vault

A fully offline, command-line password manager written in Python.  
**No cloud. No network. Your secrets stay on your machine — always.**

---

## ✨ Features

| Feature | Details |
|---|---|
| 🔑 Master Password | SHA-256 + salt hashing — never stored in plain text |
| 🔒 AES Encryption | Fernet (AES-128-CBC) via the `cryptography` library |
| 🗂️ Local Storage | All data lives in `vault.json` — fully portable |
| ➕ Add Entries | Store website, username, password, and optional notes |
| 🔍 Search | Fuzzy keyword search across all saved entries |
| ✏️ Edit / 🗑️ Delete | Full CRUD operations on every entry |
| ⚡ Generator | Random (symbols) or memorable passphrase modes |
| 💪 Strength Checker | Rates any password and gives improvement tips |
| 📋 Clipboard | Copies password directly to clipboard (via `pyperclip`) |
| 🎨 Rich CLI | Coloured ANSI terminal interface with a banner |

---

## 📁 Project Structure

```
password_vault/
├── vault.py          # Main entry point & menu loop
├── vault_crypto.py   # Hashing, key derivation, encryption/decryption
├── vault_storage.py  # JSON file I/O (CRUD for vault entries)
├── vault_ui.py       # ANSI colours, banner, prompts, menus
├── vault_utils.py    # Password generator, strength checker, clipboard
├── requirements.txt  # Third-party dependencies
├── vault.json        # Auto-created on first run (DO NOT share this file)
└── README.md
```

---

## 🚀 Quick Start

### 1. Install Python 3.10+
Download from https://www.python.org/downloads/ and ensure **"Add to PATH"** is checked.

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the vault
```bash
python vault.py
```

On **first run** you will be asked to create a Master Password.  
On subsequent runs, enter that password to unlock the vault.

---

## 🔐 Security Design

### Master Password (Hashing)
```
user password  ──┐
                  ├──▶  SHA-256(salt + password)  ──▶  stored hash
random salt    ──┘
```
The actual master password is **never written to disk** — only the hash.

### Vault Key (Key Derivation)
```
master password + salt  ──▶  PBKDF2-HMAC-SHA256 (390,000 iterations)
                          ──▶  32-byte key  ──▶  Fernet symmetric key
```
The same master password always produces the same encryption key, so no separate key file is needed.

### Stored Password (Encryption)
```
plain password  ──▶  Fernet.encrypt(key)  ──▶  base64 token  (stored in vault.json)
```

---

## ⚙️ Core Concepts Demonstrated

| Concept | Python Module | Where Used |
|---|---|---|
| File I/O | `json`, `pathlib` | `vault_storage.py` |
| SHA-256 Hashing | `hashlib` | `vault_crypto.py` |
| PBKDF2 Key Derivation | `cryptography.hazmat` | `vault_crypto.py` |
| Symmetric Encryption | `cryptography.fernet` | `vault_crypto.py` |
| CLI Menu Loop | `input()`, `getpass` | `vault.py`, `vault_ui.py` |
| Password Generation | `random`, `string` | `vault_utils.py` |
| Clipboard | `pyperclip` | `vault_utils.py` |

---

## ⚠️ Important Notes

- **Back up `vault.json`** — it contains your encrypted passwords.
- **Do NOT share `vault.json`** without understanding that it can be brute-forced if your master password is weak.
- If you forget your master password, **the vault cannot be unlocked** — there is no recovery mechanism by design.
- This project is educational. For production use, consider battle-tested managers like Bitwarden or KeePass.

---

## 📚 Learning Path

1. Read `vault_crypto.py` — understand hashing vs. encryption.
2. Read `vault_storage.py` — understand how JSON is used for local persistence.
3. Read `vault_utils.py` — explore the password generator logic.
4. Read `vault_ui.py` — learn how ANSI codes create a rich CLI.
5. Read `vault.py` — see how all modules are wired into a usable application.
