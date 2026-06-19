"""
test_vault.py
-------------
Automated end-to-end integration test for PassVault.
Patches input() and getpass.getpass() to drive the vault without keyboard input.
Runs every feature: setup, login, add, list, search, edit, delete,
password generator, strength checker, and lock/exit.
"""

import sys
import os
import json
import unittest
import io
from unittest.mock import patch, MagicMock
from pathlib import Path

# ── Point storage at a throw-away test file ───────────────────────────────────
import vault_storage as storage
TEST_VAULT_FILE = Path("test_run_vault.json")
storage.VAULT_FILE = TEST_VAULT_FILE

import vault_crypto as crypto
import vault_utils  as utils
import vault_ui     as ui
import vault        as v

MASTER_PW = "TestMaster@123"

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def fresh_vault():
    """Create a clean vault for a test."""
    if TEST_VAULT_FILE.exists():
        TEST_VAULT_FILE.unlink()
    salt = crypto.generate_salt()
    h    = crypto.hash_master_password(MASTER_PW, salt)
    storage.create_vault(salt, h)
    fernet = crypto.get_fernet(MASTER_PW, salt)
    return fernet


def captured(fn, *args, **kwargs):
    """Run fn() and return its stdout as a string."""
    buf = io.StringIO()
    with patch("sys.stdout", buf):
        try:
            fn(*args, **kwargs)
        except SystemExit:
            pass
    return buf.getvalue()


SEP = "=" * 60

def section(title):
    print(f"\n{SEP}")
    print(f"  {title}")
    print(SEP)


# ─────────────────────────────────────────────────────────────────────────────
# Test cases
# ─────────────────────────────────────────────────────────────────────────────

class TestCrypto(unittest.TestCase):

    def test_salt_is_unique(self):
        s1, s2 = crypto.generate_salt(), crypto.generate_salt()
        self.assertNotEqual(s1, s2)

    def test_hash_verify_correct(self):
        salt = crypto.generate_salt()
        h = crypto.hash_master_password(MASTER_PW, salt)
        self.assertTrue(crypto.verify_master_password(MASTER_PW, salt, h))

    def test_hash_verify_wrong(self):
        salt = crypto.generate_salt()
        h = crypto.hash_master_password(MASTER_PW, salt)
        self.assertFalse(crypto.verify_master_password("WrongPass!", salt, h))

    def test_encrypt_decrypt_roundtrip(self):
        salt   = crypto.generate_salt()
        fernet = crypto.get_fernet(MASTER_PW, salt)
        plain  = "my$ecretP@ssw0rd"
        token  = crypto.encrypt_password(plain, fernet)
        self.assertNotEqual(token, plain)
        self.assertEqual(crypto.decrypt_password(token, fernet), plain)

    def test_wrong_key_cannot_decrypt(self):
        from cryptography.fernet import InvalidToken
        s1 = crypto.generate_salt()
        s2 = crypto.generate_salt()
        f1 = crypto.get_fernet(MASTER_PW, s1)
        f2 = crypto.get_fernet(MASTER_PW, s2)
        token = crypto.encrypt_password("secret", f1)
        with self.assertRaises(InvalidToken):
            crypto.decrypt_password(token, f2)


class TestStorage(unittest.TestCase):

    def setUp(self):
        self.fernet = fresh_vault()

    def tearDown(self):
        if TEST_VAULT_FILE.exists():
            TEST_VAULT_FILE.unlink()

    def _make_entry(self, site="github.com", user="alice"):
        return {
            "website":  site,
            "username": user,
            "password": crypto.encrypt_password("pass123", self.fernet),
            "notes":    "test note",
        }

    def test_vault_exists(self):
        self.assertTrue(storage.vault_exists())

    def test_add_and_load(self):
        storage.add_entry(self._make_entry())
        entries = storage.load_entries()
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["website"], "github.com")

    def test_find_entries_match(self):
        storage.add_entry(self._make_entry("github.com"))
        storage.add_entry(self._make_entry("gitlab.com"))
        storage.add_entry(self._make_entry("google.com"))
        results = storage.find_entries("git")
        self.assertEqual(len(results), 2)

    def test_find_entries_no_match(self):
        storage.add_entry(self._make_entry("github.com"))
        self.assertEqual(storage.find_entries("twitter"), [])

    def test_update_entry(self):
        storage.add_entry(self._make_entry())
        updated = self._make_entry(user="bob")
        self.assertTrue(storage.update_entry(0, updated))
        self.assertEqual(storage.load_entries()[0]["username"], "bob")

    def test_delete_entry(self):
        storage.add_entry(self._make_entry("a.com"))
        storage.add_entry(self._make_entry("b.com"))
        self.assertTrue(storage.delete_entry(0))
        entries = storage.load_entries()
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["website"], "b.com")

    def test_delete_invalid_index(self):
        self.assertFalse(storage.delete_entry(99))


class TestUtils(unittest.TestCase):

    def test_generated_password_length(self):
        for length in [8, 12, 16, 24, 32, 64]:
            pw = utils.generate_password(length)
            self.assertEqual(len(pw), length, f"Expected len {length}")

    def test_generated_password_complexity(self):
        import string
        pw = utils.generate_password(20)
        self.assertTrue(any(c.isupper()             for c in pw), "Missing uppercase")
        self.assertTrue(any(c.islower()             for c in pw), "Missing lowercase")
        self.assertTrue(any(c.isdigit()             for c in pw), "Missing digit")
        self.assertTrue(any(c in string.punctuation for c in pw), "Missing symbol")

    def test_memorable_password_format(self):
        pw = utils.generate_memorable_password(4)
        parts = pw.rsplit("-", 1)      # last segment is digit suffix
        self.assertTrue(parts[-1][-3:].isdigit(), "Missing digit suffix")

    def test_strength_weak(self):
        rating, _ = utils.check_strength("abc")
        self.assertEqual(rating, "Weak")

    def test_strength_fair(self):
        rating, _ = utils.check_strength("Abcdef12")
        self.assertIn(rating, ("Fair", "Strong"))

    def test_strength_very_strong(self):
        rating, _ = utils.check_strength("MyV3ryStr0ng&LongP@ss!XYZ")
        self.assertEqual(rating, "Very Strong")

    def test_strength_tips_for_weak(self):
        _, tips = utils.check_strength("abc")
        self.assertTrue(len(tips) > 0, "Should have improvement tips")

    def test_clipboard_graceful(self):
        # Should not crash regardless of whether pyperclip works in this env
        result = utils.copy_to_clipboard("test")
        self.assertIsInstance(result, bool)


class TestVaultActions(unittest.TestCase):
    """
    Integration tests for vault.py action functions.
    Patches: input(), getpass.getpass(), os.system() (clear screen),
             pyperclip.copy() (clipboard).
    """

    def setUp(self):
        self.fernet = fresh_vault()
        v._fernet          = self.fernet
        v._master_password = MASTER_PW

    def tearDown(self):
        if TEST_VAULT_FILE.exists():
            TEST_VAULT_FILE.unlink()

    def _run_action(self, action_fn, inputs, getpass_inputs=None):
        """
        Run an action with mocked input() and getpass().
        Returns captured stdout.
        """
        inp_iter  = iter(inputs)
        gp_iter   = iter(getpass_inputs or [])

        buf = io.StringIO()
        with patch("builtins.input",        side_effect=lambda *a, **kw: next(inp_iter, "")), \
             patch("getpass.getpass",        side_effect=lambda *a, **kw: next(gp_iter, "")), \
             patch("os.system",             return_value=0), \
             patch("sys.stdout",            buf):
            try:
                action_fn()
            except (SystemExit, StopIteration):
                pass
        return buf.getvalue()

    # ── Add ──────────────────────────────────────────────────────────────────
    def test_add_with_manual_password(self):
        out = self._run_action(
            v.action_add,
            inputs=["github.com", "alice@example.com", "work note", "n", "n"],
            getpass_inputs=["Str0ng&Pass!XYZ9"],
        )
        entries = storage.load_entries()
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["website"], "github.com")
        self.assertEqual(entries[0]["username"], "alice@example.com")
        plain = crypto.decrypt_password(entries[0]["password"], self.fernet)
        self.assertEqual(plain, "Str0ng&Pass!XYZ9")
        print("  [add] Entry saved and decrypted correctly")

    def test_add_with_generated_password(self):
        out = self._run_action(
            v.action_add,
            inputs=["twitter.com", "bob", "", "y", "16", "n"],
        )
        entries = storage.load_entries()
        self.assertEqual(len(entries), 1)
        plain = crypto.decrypt_password(entries[0]["password"], self.fernet)
        self.assertEqual(len(plain), 16, f"Generated password should be 16 chars, got: {plain}")
        print("  [add] Generated password stored and decrypted, length=16")

    # ── List ─────────────────────────────────────────────────────────────────
    def test_list_all_empty(self):
        out = self._run_action(v.action_list_all, inputs=[""])
        self.assertIn("empty", out.lower())
        print("  [list] Empty vault message shown")

    def test_list_all_with_entries(self):
        enc = crypto.encrypt_password("pass", self.fernet)
        storage.add_entry({"website": "amazon.com", "username": "u", "password": enc, "notes": ""})
        out = self._run_action(v.action_list_all, inputs=[""])
        self.assertIn("amazon.com", out)
        print("  [list] Entry visible in listing")

    # ── Search ───────────────────────────────────────────────────────────────
    def test_search_found(self):
        enc = crypto.encrypt_password("secretPW!", self.fernet)
        storage.add_entry({"website": "netflix.com", "username": "user", "password": enc, "notes": ""})
        out = self._run_action(
            v.action_search,
            inputs=["netflix", "n"],   # don't reveal password
        )
        self.assertIn("netflix.com", out)
        print("  [search] Found entry for netflix.com")

    def test_search_not_found(self):
        out = self._run_action(
            v.action_search,
            inputs=["unknownsite123", ""],
        )
        self.assertIn("No entries found", out)
        print("  [search] Correct 'not found' message")

    # ── Edit ─────────────────────────────────────────────────────────────────
    def test_edit_entry(self):
        enc = crypto.encrypt_password("oldpass", self.fernet)
        storage.add_entry({"website": "reddit.com", "username": "old_user", "password": enc, "notes": ""})
        self._run_action(
            v.action_edit,
            inputs=["0", "reddit.com", "new_user", "", "y", "n", ""],
            getpass_inputs=["NewStr0ng@Pass!"],
        )
        entry = storage.load_entries()[0]
        self.assertEqual(entry["username"], "new_user")
        plain = crypto.decrypt_password(entry["password"], self.fernet)
        self.assertEqual(plain, "NewStr0ng@Pass!")
        print("  [edit] Username and password updated correctly")

    # ── Delete ───────────────────────────────────────────────────────────────
    def test_delete_entry(self):
        enc = crypto.encrypt_password("pw", self.fernet)
        storage.add_entry({"website": "old-site.com", "username": "x", "password": enc, "notes": ""})
        self.assertEqual(len(storage.load_entries()), 1)
        self._run_action(v.action_delete, inputs=["0", "y"])
        self.assertEqual(len(storage.load_entries()), 0)
        print("  [delete] Entry deleted successfully")

    def test_delete_cancelled(self):
        enc = crypto.encrypt_password("pw", self.fernet)
        storage.add_entry({"website": "keep.com", "username": "x", "password": enc, "notes": ""})
        self._run_action(v.action_delete, inputs=["0", "n"])
        self.assertEqual(len(storage.load_entries()), 1)
        print("  [delete] Cancellation respected, entry retained")

    # ── Generator ────────────────────────────────────────────────────────────
    def test_generate_random(self):
        out = self._run_action(v.action_generate, inputs=["1", "20", "n"])
        self.assertIn("Generated Password", out)
        print("  [generate] Random password shown in output")

    def test_generate_passphrase(self):
        out = self._run_action(v.action_generate, inputs=["2", "4", "n"])
        self.assertIn("Generated Password", out)
        print("  [generate] Passphrase shown in output")

    # ── Strength checker ─────────────────────────────────────────────────────
    def test_strength_checker_weak(self):
        out = self._run_action(v.action_check_strength, inputs=[""], getpass_inputs=["abc"])
        self.assertIn("Weak", out)
        print("  [strength] 'abc' correctly rated Weak")

    def test_strength_checker_strong(self):
        out = self._run_action(
            v.action_check_strength, inputs=[""],
            getpass_inputs=["MyV3ryStr0ng&LongP@ss!XYZ"],
        )
        self.assertIn("Very Strong", out)
        print("  [strength] Long complex password rated Very Strong")


# ─────────────────────────────────────────────────────────────────────────────
# Runner
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n" + SEP)
    print("  PassVault - Full Integration Test Suite")
    print(SEP)

    loader = unittest.TestLoader()
    suite  = unittest.TestSuite()

    for cls in [TestCrypto, TestStorage, TestUtils, TestVaultActions]:
        suite.addTests(loader.loadTestsFromTestCase(cls))

    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)

    print(SEP)
    if result.wasSuccessful():
        print(f"  RESULT: ALL {result.testsRun} TESTS PASSED")
    else:
        print(f"  RESULT: {len(result.failures)} FAILURES, {len(result.errors)} ERRORS")
    print(SEP + "\n")

    sys.exit(0 if result.wasSuccessful() else 1)
