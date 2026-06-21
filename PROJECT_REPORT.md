# 📊 PassVault — Project Report & Architecture Flow

This document is designed to help you explain the **PassVault** project to others (such as classmates, teachers, or interviewers). It breaks down the technical architecture, the cryptography used, and the step-by-step data flow.

---

## 1. Executive Summary
**PassVault** is a local, offline command-line password manager written in Python. 
Its primary goal is to solve the security risk of cloud-based password managers by keeping all sensitive data strictly on the user's local machine. It provides a secure, encrypted vault to store website credentials, ensuring that even if the physical device is compromised, the data remains unreadable without the Master Password.

---

## 2. Technology Stack
* **Language:** Python 3.12+
* **Core Libraries:**
  * `cryptography` (Fernet, PBKDF2HMAC) — For industry-standard encryption and key derivation.
  * `hashlib` — For secure, one-way hashing (SHA-256).
  * `json` — For structuring and storing local data.
  * `pyperclip` — For clipboard integration.
  * `os`, `sys`, `getpass` — For terminal manipulation and secure password input.

---

## 3. The Step-by-Step Data Flow

When explaining how the vault works, the most important part is the **Cryptographic Flow**. Here is exactly what happens behind the scenes step-by-step.

### A. First-Time Setup (Vault Creation)
1. **User Input:** The user types a Master Password.
2. **Salt Generation:** The app generates a 32-byte random "salt" (a random string of data).
3. **Master Hashing:** The Master Password + Salt are hashed together using **SHA-256**. 
4. **Storage:** Only the *Hash* and the *Salt* are saved to `vault.json`. The actual Master Password is instantly deleted from the computer's memory.

### B. Logging In (Authentication)
1. **User Input:** The user types their Master Password to unlock the vault.
2. **Verification:** The app takes the typed password, mixes it with the saved *Salt*, and hashes it.
3. **Comparison:** If the resulting hash matches the saved *Hash* in `vault.json`, access is granted.

### C. Deriving the Encryption Key
*We need a key to encrypt the passwords, but we cannot save this key on the hard drive, otherwise a hacker could find it!*
1. **Key Derivation (PBKDF2):** Once logged in, the app takes the Master Password and the Salt and runs them through a PBKDF2 function 390,000 times.
2. **The Result:** This generates a highly secure 32-byte symmetric key.
3. **Usage:** This key is kept only in RAM (temporary memory) while the app is open. When the app closes, the key vanishes.

### D. Saving a New Password (Encryption)
1. **User Input:** The user enters a website, username, and a plain-text password (e.g., `apple123`).
2. **Encryption:** The app uses the derived key and the **Fernet (AES-128-CBC)** algorithm to scramble `apple123` into an unreadable token (e.g., `gAAAAABk...`).
3. **Storage:** The app saves the website, username, and the *scrambled token* into `vault.json`.

### E. Retrieving a Password (Decryption)
1. **Search:** The user searches for "Apple".
2. **Decryption:** The app grabs the scrambled token from `vault.json`.
3. **Unlocking:** Using the key held in RAM, the app decrypts the token back into `apple123` and displays it on the screen or copies it to the clipboard.

---

## 4. Code Structure Breakdown

If someone asks how your code is organized, you can explain that it is split into 5 modular files to follow the "Separation of Concerns" principle:

| Module | Purpose |
|---|---|
| **`vault.py`** | The "Brain". It runs the main menu loop and connects the UI to the storage and cryptography. |
| **`vault_crypto.py`** | The "Locksmith". Handles all SHA-256 hashing, PBKDF2 key derivation, and Fernet AES encryption. |
| **`vault_storage.py`** | The "Filing Cabinet". Reads and writes the JSON dictionaries to the hard drive. |
| **`vault_utils.py`** | The "Tools". Generates random passwords, checks password strength, and handles the clipboard. |
| **`vault_ui.py`** | The "Paintbrush". Handles the colorful ASCII banners, menus, and user prompts in the terminal. |

---

## 5. Key Talking Points for Presentations/Interviews
If you are presenting this project, hit these key points:
* *"I used **PBKDF2** with 390,000 iterations to derive the encryption key, which protects against brute-force attacks."*
* *"The system is **Zero-Knowledge**. The master password is never written to disk, only a salted SHA-256 hash."*
* *"I structured the data using **JSON** because it is lightweight, human-readable, and easy to parse in Python."*
* *"I built a custom **Command Line Interface (CLI)** using ANSI escape codes to make the terminal experience colorful and user-friendly without needing heavy GUI libraries."*
