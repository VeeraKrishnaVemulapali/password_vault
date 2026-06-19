"""
vault_utils.py
--------------
Password generator and clipboard helper for the Password Vault.
"""

import random
import string

try:
    import pyperclip
    _CLIPBOARD_AVAILABLE = True
except ImportError:
    _CLIPBOARD_AVAILABLE = False


# ──────────────────────────────────────────────────────────────────────────────
# Password generator
# ──────────────────────────────────────────────────────────────────────────────

def generate_password(length: int = 16) -> str:
    """
    Generate a cryptographically strong random password.

    Guarantees at least:
      - 1 uppercase letter
      - 1 lowercase letter
      - 1 digit
      - 1 special character

    Args:
        length: Desired password length (minimum 8).

    Returns:
        A random password string.
    """
    length = max(length, 8)  # enforce a sensible minimum

    alphabet = string.ascii_letters + string.digits + string.punctuation

    # Ensure each character category is represented
    mandatory = [
        random.choice(string.ascii_uppercase),
        random.choice(string.ascii_lowercase),
        random.choice(string.digits),
        random.choice(string.punctuation),
    ]

    rest = [random.choice(alphabet) for _ in range(length - len(mandatory))]
    combined = mandatory + rest
    random.shuffle(combined)
    return "".join(combined)


def generate_memorable_password(words: int = 4) -> str:
    """
    Generate a passphrase-style password (word1-word2-word3-word4 + digits).
    Uses a small built-in word list for zero external dependencies.
    """
    word_list = [
        "apple", "bridge", "castle", "delta", "eagle", "forest", "garden",
        "harbor", "island", "jungle", "knight", "lemon", "mango", "needle",
        "ocean", "planet", "queen", "river", "shadow", "tiger", "umbrella",
        "valley", "winter", "xenon", "yellow", "zipper", "anchor", "breeze",
        "cloud", "dagger", "ember", "flame", "gravel", "hollow", "ivory",
    ]
    chosen = random.choices(word_list, k=words)
    suffix = str(random.randint(100, 999))
    return "-".join(chosen) + suffix


# ──────────────────────────────────────────────────────────────────────────────
# Clipboard
# ──────────────────────────────────────────────────────────────────────────────

def copy_to_clipboard(text: str) -> bool:
    """
    Copy *text* to the system clipboard.
    Returns True if successful, False if pyperclip is not available.
    """
    if _CLIPBOARD_AVAILABLE:
        pyperclip.copy(text)
        return True
    return False


def clipboard_available() -> bool:
    return _CLIPBOARD_AVAILABLE


# ──────────────────────────────────────────────────────────────────────────────
# Password strength checker
# ──────────────────────────────────────────────────────────────────────────────

def check_strength(password: str) -> tuple[str, list[str]]:
    """
    Evaluate the strength of a password.

    Returns:
        (rating, tips) where rating is one of 'Weak', 'Fair', 'Strong', 'Very Strong'
        and tips is a list of improvement suggestions.
    """
    tips: list[str] = []
    score = 0

    if len(password) >= 8:
        score += 1
    else:
        tips.append("Use at least 8 characters.")

    if len(password) >= 16:
        score += 1
    else:
        tips.append("Aim for 16+ characters for better security.")

    if any(c.isupper() for c in password):
        score += 1
    else:
        tips.append("Add uppercase letters (A-Z).")

    if any(c.islower() for c in password):
        score += 1
    else:
        tips.append("Add lowercase letters (a-z).")

    if any(c.isdigit() for c in password):
        score += 1
    else:
        tips.append("Include numbers (0-9).")

    if any(c in string.punctuation for c in password):
        score += 1
    else:
        tips.append("Include special characters (!@#$...).")

    rating_map = {0: "Weak", 1: "Weak", 2: "Fair", 3: "Fair", 4: "Strong", 5: "Strong", 6: "Very Strong"}
    return rating_map[score], tips
