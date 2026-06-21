# 📖 PassVault — User Guide

Welcome to **PassVault**! This guide explains the purpose of the application and provides a clear, step-by-step walkthrough on how to use it day-to-day.

---

## 🎯 The Purpose of PassVault

PassVault is an **Offline Password Manager**. 

Most modern password managers (like LastPass or 1Password) store your passwords on the cloud (the internet). While convenient, it means your data is on someone else's server. 

**PassVault is different:**
* **100% Offline:** It never connects to the internet.
* **Total Control:** Your passwords live entirely on your computer inside an encrypted file (`vault.json`).
* **Highly Secure:** It uses military-grade encryption (AES-128-CBC) to lock your passwords. Even if a hacker steals your computer, they cannot read your passwords without your Master Password.

---

## 🚀 Step-by-Step Instructions

### Step 1: Starting the Application
You can start the vault in one of two ways:
* **The Easy Way:** Double-click the `Launch_Vault.bat` shortcut located on your Desktop.
* **The Terminal Way:** Open Command Prompt, type `cd E:\Projects\password_vault`, and then type `python vault.py`.

*When the app opens, you will see a welcome splash screen. Press **Enter** to proceed.*

### Step 2: First-Time Setup
If this is your first time opening PassVault:
1. The system will ask you to create a **Master Password**.
2. Type a password that is strong but that you will definitely remember. *(Note: The screen will not show `***` as you type; it remains blank for security. Just type and press Enter.)*
3. Type it a second time to confirm.

> ⚠️ **CRITICAL WARNING:** There is **NO "Forgot Password"** button! Because this app is completely offline, there is no email recovery. If you forget this Master Password, you will permanently lose access to all your saved passwords.

### Step 3: Logging In
On all future visits, the app will simply ask for your Master Password to unlock the vault. You have 3 attempts before it locks you out for that session.

---

## 🎛️ Using the Main Menu

Once unlocked, you will see the main menu. To select an option, type the corresponding number and press **Enter**.

### Option 1: Add a new password entry
*Use this when you sign up for a new website.*
1. Enter the website name (e.g., `Netflix`).
2. Enter your username or email.
3. The app will ask: *Generate a secure password automatically?* 
   * If you type `y`, it creates a strong, random password for you.
   * If you type `n`, you can type in your own password.
4. The app will save the entry and offer to copy the password to your clipboard so you can paste it into the website.

### Option 2: Search / retrieve a password
*Use this when you need to log into a website.*
1. Type part of the website name (e.g., `net` for Netflix).
2. It will display the account, but hide the password for privacy.
3. It will ask: *Reveal password(s)?* Type `y` to see it on screen.
4. It will then offer to copy it to your clipboard for easy pasting.

### Option 3: List all entries
This simply prints out every account you have saved in your vault. Passwords remain hidden by default so nobody looking over your shoulder can see them.

### Option 4: Edit an existing entry
*Use this if you change your password on a website or want to update your username.*
1. It will list your accounts and ask for the **number** in the brackets `[ ]` next to the account you want to change.
2. It will ask for the new website, username, and password. If you want to keep the old value for a field, just leave it blank and press Enter.

### Option 5: Delete an entry
*Use this if you close an account and want to remove it from your vault.*
1. Provide the bracketed number `[ ]` of the account.
2. Confirm the deletion by typing `y`.

### Option 6 & 7: Password Tools
* **Generate a secure password:** Creates a strong password and copies it to your clipboard without saving it to the vault. Great for temporary needs!
* **Check password strength:** Type in any password, and the vault will tell you how strong it is and give you tips to improve it.

### Option 8: Lock & Exit
**Always use this when you are done.** This safely closes the application and ensures your vault is locked.

---

## 🛡️ Best Practices & Maintenance

* **Backup your vault:** Your encrypted passwords are saved in a file called `vault.json` in the `E:\Projects\password_vault` folder. You should occasionally copy this file to a safe USB drive. If your computer crashes, you can install PassVault on a new computer, paste your `vault.json` file into the folder, and all your passwords will be restored!
* **Do NOT delete `vault.json`:** If you delete this file, your passwords are gone forever.
