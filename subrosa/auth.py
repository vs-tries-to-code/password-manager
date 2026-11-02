import bcrypt
import questionary
from .crypto import *
from rich.console import Console
from rich.table import Table

console = Console()

MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_BYTES = 72    # bcrypt cannot handle more than this

def create_master_passwd():
    console.print("\n[plum1]--- Create Master Password ---[/plum1]")

    pw1 = questionary.password("Enter master password: ").ask()
    if pw1 is None: #user clicked ctrl+C
        return None

    #too short
    if len(pw1) < MIN_PASSWORD_LENGTH:
        console.print(f"\n[red]Use at least {MIN_PASSWORD_LENGTH} characters.[/red]")
        return None

    #too long for bcrypt
    if len(pw1.encode("utf-8")) > MAX_PASSWORD_BYTES:
        console.print(f"\n[red]Use at most {MAX_PASSWORD_BYTES} bytes.[/red]")
        return None

    #confirmation
    pw2 = questionary.password("Confirm password: ").ask()
    if pw2 is None:
        return None

    # matching entries
    if pw1 != pw2:
        console.print("\n[red]Passwords do not match.[/red]")
        return None

    return pw1

def hash_pw(passwd: str) -> bytes:
    pw_bytes = passwd.encode('utf-8')
    return bcrypt.hashpw(pw_bytes, bcrypt.gensalt())

def verify_pw(passwd: str, stored_hash: bytes) -> bool:
    
    return bcrypt.checkpw(passwd.encode('utf-8'), stored_hash)

MAX_ATTEMPTS = 5

def login(stored_hash, stored_salt, vault_key_encryp):
    attempts = 0
    while attempts < MAX_ATTEMPTS:
        pw = questionary.password("Enter master password: ").ask()
        if pw is None:
            return None
        if verify_pw(pw, stored_hash):
            wrapping_key = derive_key(pw, stored_salt)
            try:
                vault_key = decrypt(vault_key_encryp, wrapping_key).encode('utf-8')
                return vault_key
            except Exception:
                    console.print("\n[bold red]Vault integrity error — cannot unwrap key.[/bold red]")
                    return None

        attempts += 1

        console.print(
            "\n[red]Incorrect password.[/red]"
            f"\n[red]{MAX_ATTEMPTS - attempts} attempts remaining.[/red]"
        )

    return None

    




