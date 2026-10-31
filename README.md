# Sub Rosa

A terminal-based password manager written in Python. Your passwords are stored in a local SQLite database, encrypted with a key that only your master password can unlock.

> *Sub rosa* is Latin for "in secret". The tool's motto is a fair warning: **forget the master password, and you are done for.** There is no recovery option.

---

## Features

- Add, edit, and fetch credentials (website, username, password) from an interactive menu
- Master password protected by **bcrypt** hashing
- Every saved password is encrypted with **Fernet** (AES-128-CBC with an HMAC-SHA256 integrity check)
- **Envelope encryption**: changing your master password does not require re-encrypting your whole vault
- Login attempt limit (5 tries per launch)
- Everything stays on your machine, with no network access and no cloud

---

## Requirements

- Python 3.9 or newer
- Linux, macOS, or Windows (any terminal)

All Python dependencies (`bcrypt`, `cryptography`, `rich`, `questionary`, `pyfiglet`) are installed automatically along with the tool. You do not need to install them yourself.

---

## Installation

First, get the code:

```bash
git clone <your-repo-url>
cd password-manager
```

Then pick **one** of the options below.

### Option 1: Install as a command with uv (recommended)

[uv](https://docs.astral.sh/uv/) installs the tool into its own isolated environment and puts the `subrosa` command on your PATH, so you can run it from any folder.

```bash
uv tool install .
subrosa
```

### Option 2: Run from the project folder with uv

```bash
uv sync          # creates .venv and installs all dependencies
uv run subrosa   # runs the tool
```

### Option 3: Plain pip

```bash
python -m venv .venv

# Activate the virtual environment:
source .venv/bin/activate        # Linux / macOS
.venv\Scripts\activate           # Windows

pip install .
subrosa
```

### For development

Use an editable install so your code changes take effect without reinstalling:

```bash
pip install -e .      # or: uv sync
```

---

## Usage

Run the tool:

```bash
subrosa
```

**First launch:** you are asked to create a master password (entered twice to confirm). This sets up your vault.

**Later launches:** you are asked for your master password. You get 5 attempts before the program exits.

Once logged in, you see a menu:

| Option | What it does |
|---|---|
| **1. Add Entry** | Save a new website, username, and password |
| **2. Edit Password** | Replace the saved password for a website |
| **3. Fetch Password** | Look up a website and show its decrypted credentials |
| **4. Update Master Password** | Change your master password (you must log in again first) |
| **5. Exit** | Close the vault |

Website names are not case sensitive (`GitHub` and `github` are treated as the same site).

---

## How it works

This section explains the design from the ground up. You do not need to read it to use the tool, but it shows why the tool can be trusted.

### The problem

We need to store passwords so that:

1. Someone who steals the database file **cannot read them**.
2. You can **change your master password** without losing your saved passwords.

### Building block 1: hashing the master password (bcrypt)

A *hash* is a one-way scrambling function. You can turn `"hello"` into a long string, but you cannot turn that string back into `"hello"`.

When you create your master password, Sub Rosa stores only its bcrypt hash. At login it hashes what you typed and compares the result. Your real master password is never saved anywhere.

bcrypt puts its own random salt inside the hash string, so you do not need to store it separately.

### Building block 2: turning a password into a key (PBKDF2)

Encryption needs a *key*, which is 32 random-looking bytes, not a memorable password. PBKDF2 converts your master password into such a key by mixing in a random **salt** and repeating the work 100,000 times. The repeated work makes guessing passwords slow for an attacker.

The salt is stored in the database. It is not secret, but you need the same salt each time to get the same key back.

### Building block 3: envelope encryption

If your master password directly produced the key that encrypts your vault, changing the password would change the key, and all your old entries would become unreadable.

To avoid this, Sub Rosa uses two keys:

- **Vault key**: a random key generated once when you set up the vault. It encrypts and decrypts your saved passwords. It never changes, and it has no mathematical link to your master password.
- **Wrapping key**: derived from your master password and salt using PBKDF2. Its only job is to lock and unlock the vault key.

Think of the vault key as a house key and the wrapping key as a lockbox around it. Changing your master password means taking the house key out of the old lockbox and putting it in a new one. The house key itself never changes, so every saved entry still opens.

```
  Master password + salt
           |
           |  PBKDF2
           v
     Wrapping key ──── locks/unlocks ───▶ Vault key (stored encrypted)
                                               |
                                               |  encrypts/decrypts
                                               v
                                    Saved passwords (stored encrypted)
```

### The login flow

1. You type your master password.
2. bcrypt checks it against the stored hash.
3. PBKDF2 derives the wrapping key from the password and the stored salt.
4. The wrapping key unlocks the vault key.
5. The vault key is held in memory only, and it is used for every add, edit, and fetch while you are logged in.

### The password-change flow

1. You log in again (proves it is really you).
2. You enter and confirm a new master password.
3. A new bcrypt hash, a new salt, and a new wrapping key are created.
4. The **same vault key** is re-locked with the new wrapping key.
5. The new hash, salt, and locked vault key are written to the database in a single operation.

---

## Where your data lives

The database is a single SQLite file:

```
~/.subrosa/storage.db
```

(`~` means your home directory. On Windows this is `C:\Users\<you>\.subrosa\storage.db`.)

It has two tables:

| Table | Columns | Notes |
|---|---|---|
| `master_auth` | `password_hash`, `encryption_salt`, `vault_key_encryp` | One row. The vault key is stored **encrypted**. |
| `vault` | `website`, `username`, `password` | One row per saved login. The password is stored **encrypted**. |

The file itself is a normal, unencrypted SQLite file. Website names and usernames are visible to anyone who can read it. Only the passwords (and the vault key) are encrypted. Protect the folder with your operating system's file permissions, and consider backing it up somewhere safe.

To reset everything and start fresh, delete the folder:

```bash
rm -rf ~/.subrosa
```

**This permanently destroys all saved passwords.**

---

## Project structure

```
password-manager/
├── pyproject.toml        # Project metadata, dependencies, and the `subrosa` command
├── README.md
├── uv.lock               # Exact dependency versions (when using uv)
└── subrosa/
    ├── __init__.py       # Marks this folder as a Python package
    ├── app.py            # Menu, startup, and setup/login flow
    ├── auth.py           # Master password creation, hashing, and login
    ├── crypto.py         # Salt, key derivation, and encrypt/decrypt helpers
    └── database.py       # All SQLite reads and writes
```

How `pyproject.toml` works: it lists the dependencies (installed automatically) and contains this line:

```toml
[project.scripts]
subrosa = "subrosa.app:main"
```

This tells the installer to create a `subrosa` command that runs the `main()` function inside `subrosa/app.py`.

---

## Security notes and limitations

- **No password recovery.** If you forget the master password, the vault cannot be opened. There is no reset.
- **The attempt limit only protects the running program.** If someone copies `storage.db` and attacks it on their own computer, the 5-attempt limit does not apply. What protects you then is the strength of your master password, plus bcrypt and PBKDF2 making each guess slow. Use a long, unique master password.
- **Metadata is not encrypted.** Website names and usernames are stored as plain text.
- **Passwords appear on screen** when you fetch them, so be mindful of shoulder surfing and screen recordings.
- **One entry per website is assumed.** Fetching shows the first match, and editing updates every entry saved under that website name.
- This is a learning project. It follows standard practice, but it has not had a professional security audit. For critical accounts, a well-established password manager is the safer choice.

---

## Troubleshooting

| Problem | Likely cause and fix |
|---|---|
| `ModuleNotFoundError: No module named 'rich'` (or `questionary`, `pyfiglet`) | Dependencies are not installed in the active environment. Reinstall with `uv sync` or `pip install .`. |
| `ModuleNotFoundError: No module named 'app'` | An old install left a stale launcher. Reinstall: `uv sync --reinstall-package subrosa` or `pip install --force-reinstall .`. |
| `attempted relative import with no known parent package` | You ran a file directly (`python app.py`). Run `subrosa` or `python -m subrosa.app` instead. |
| `subrosa: command not found` | The environment is not activated, or the install did not finish. Activate your venv, or use `uv run subrosa`. |
| `Decryption failed` shown in a result | The entry was encrypted with a different vault key, for example if the database was replaced or edited by hand. |
| Vault looks empty after reinstalling | You are probably looking at a different database file. Check that `~/.subrosa/storage.db` is the one you expect. |

---

## Built with

- [bcrypt](https://pypi.org/project/bcrypt/) for master password hashing
- [cryptography](https://cryptography.io/) for Fernet encryption
- [questionary](https://pypi.org/project/questionary/) for interactive prompts
- [rich](https://github.com/Textualize/rich) and [pyfiglet](https://pypi.org/project/pyfiglet/) for the terminal interface
- SQLite (Python standard library) for storage