"""
vault_crypto.py
---------------
Handles all cryptographic operations for the Password Vault:
  - Master-password hashing & verification (SHA-256 + salt)
  - Fernet symmetric key derivation from the master password
  - Encrypt / decrypt individual password entries
"""

import hashlib
import os
import base64

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes


# ──────────────────────────────────────────────────────────────────────────────
# Master-password helpers
# ──────────────────────────────────────────────────────────────────────────────

def generate_salt() -> str:
    """Return a fresh 32-byte hex salt string."""
    return os.urandom(32).hex()


def hash_master_password(password: str, salt: str) -> str:
    """
    Hash *password* with *salt* using SHA-256.
    Returns the hex digest.
    """
    salted = (salt + password).encode("utf-8")
    return hashlib.sha256(salted).hexdigest()


def verify_master_password(password: str, salt: str, stored_hash: str) -> bool:
    """Return True if *password* matches *stored_hash*."""
    return hash_master_password(password, salt) == stored_hash


# ──────────────────────────────────────────────────────────────────────────────
# Fernet key derivation
# ──────────────────────────────────────────────────────────────────────────────

def derive_fernet_key(password: str, salt: str) -> bytes:
    """
    Derive a URL-safe base64-encoded 32-byte key from *password* and *salt*
    using PBKDF2-HMAC-SHA256.  This key is used with Fernet.
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=bytes.fromhex(salt),
        iterations=390_000,   # NIST-recommended minimum (2023)
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode("utf-8")))


def get_fernet(password: str, salt: str) -> Fernet:
    """Return a Fernet instance keyed from *password* and *salt*."""
    return Fernet(derive_fernet_key(password, salt))


# ──────────────────────────────────────────────────────────────────────────────
# Encrypt / decrypt
# ──────────────────────────────────────────────────────────────────────────────

def encrypt_password(plain_text: str, fernet: Fernet) -> str:
    """Encrypt *plain_text* and return a base64 token string."""
    return fernet.encrypt(plain_text.encode("utf-8")).decode("utf-8")


def decrypt_password(token: str, fernet: Fernet) -> str:
    """Decrypt *token* and return the original plain-text string."""
    return fernet.decrypt(token.encode("utf-8")).decode("utf-8")
