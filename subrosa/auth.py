import bcrypt
import questionary
from .crypto import *
from rich.console import Console
from rich.table import Table

console = Console()

def create_master_passwd():
    console.print("\n[plum1]--- Create Master Password ---[/plum1]")
    pw1 = questionary.password("Enter master password: ").ask()
    pw2 = questionary.password("Confirm password: ").ask()

    if pw1 == pw2:
        return pw1

    console.print("\n[red]--- Passwords do not match, try again. ---[/red]")
    return None

def set_new_mp():
    console.print("\n[plum1]--- Change Master Password ---[/plum1]")
    pw1 = questionary.password("Enter new master password: ").ask()
    pw2 = questionary.password("Confirm password: ").ask()

    if pw1 == pw2:
        return pw1

    console.print("\n[red]--- Passwords do not match, try again. ---[/red]")
    return None

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

    




