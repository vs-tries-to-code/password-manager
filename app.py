from auth import create_master_passwd, hash_pw, verify_pw, login
from crypto import derive_salt, derive_key, encrypt, decrypt
from database import create_db_connection, create_tables, master_pw_exists, add_master_pw, get_master_auth, add_vault_entry, get_vault_entries, update_entry,update_master_pw
import os
import sys
import questionary
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def display_header():
    console.print(
        Panel.fit(
            "[bold cyan]SUB ROSA[/bold cyan]\n[dim]Forget the master password, and you are done for[/dim]",
            padding=(0, 4),
            )
    )

def menu(link, key):
        while True:
            clear_screen()
            display_header()
            
            choice = questionary.select(
                "Select any one option"
                choices = [
                    "1. Add Entry", 
                    "2. Edit password",
                    "3. Fetch password",
                    "4. Update master password",
                    "5. Exit"
                    ]
                ).ask()
            
            if choice is None or "Exit" in choice:
                console.print("\n[yellow]Exiting vault. Forget the master password and you are done for[/yellow]")
                sys.exit()

            elif "Add Entry" in choice:
                console.print("\n[bold cyan]--- Add New Credentials ---[/bold cyan]")
                website = questionary.text("Website / Service name:").ask()
                username = questionary.text("Username / Email:").ask()
                pw = questionary.password("Password:").ask()

                if website and username and pw:
                    ciphertext = encrypt(pw, key)
                    add_vault_entry(link, website, username, ciphertext)
                    console.print(
                        f"\n[bold green]✓ Entry for '{website}' saved successfully![/bold green]"
                    )
                else:
                    console.print("\n[bold red]✗ Input cancelled or empty.[/bold red]")

                questionary.press_any_key_to_continue().ask()
            
            elif "Edit Password" in choice:
                console.print("\n[bold cyan]--- Edit Password ---[/bold cyan]")
                website = questionary.text("Enter website name to update:").ask()

                if website:
                    pw = questionary.password("Enter new password:").ask()
                    if pw:
                        ciphertext = encrypt(pw, key)
                        update_entry(link, website, ciphertext)
                        console.print(
                            f"\n[bold green]✓ Password for '{website}' updated successfully![/bold green]"
                        )

                questionary.press_any_key_to_continue().ask()

            elif "Fetch Password" in choice:
                console.print("\n[bold cyan]--- Fetch Credentials ---[/bold cyan]")
                website = questionary.text("Enter website name:").ask()

                if website:
                    entry = get_vault_entries(link, website)
                    if entry:
                        #direct unpacking since fetchone() returns a single tuple
                        web, uname, pw_cipher = entry

                        table = Table(title=f"Results for '{website}'", border_style="dim")
                        table.add_column("Website", style="cyan")
                        table.add_column("Username", style="yellow")
                        table.add_column("Decrypted Password", style="bold green")

                        try:
                            d_cipher = decrypt(pw_cipher, key)
                            table.add_row(web, uname, d_cipher)
                        except Exception:
                            table.add_row(web, uname, "[red]Decryption failed[/red]")

                        console.print(table)
                    else:
                        console.print(f"\n[bold red]✗ No entries found for '{website}'.[/bold red]")

                questionary.press_any_key_to_continue().ask()

            elif "Update Master Password" in choice:
            console.print("\n[bold cyan]--- Update Master Password ---[/bold cyan]")
            stored_hash, stored_salt = get_master_auth(link)

            #re-authenticate before allowing master password change
            k = login(stored_hash, stored_salt)
            if k is not None:
                new_mp = set_new_mp()
                if new_mp:
                    hashed_pw = hash_pw(new_mp)
                    new_salt = derive_salt()
                    add_master_pw(link, hashed_pw, new_salt)
                    console.print(
                        "\n[bold green]✓ Master Password updated!\nPlease restart the app.[/bold green]"
                    )
                    sys.exit()
            else:
                console.print(
                    "\n[bold red]✗ Verification failed.\nMaster password change aborted.[/bold red]"
                )

            questionary.press_any_key_to_continue().ask()

def main():
    clear_screen()
    display_header()
    link = create_db_connection()

    # Flow for returning user with a master password configured
    if master_pw_exists(link):
        stored_hash, stored_salt = get_master_auth(link)
        if not stored_hash or not stored_salt:
            console.print(
                "[bold red]Error loading master password from database.[/bold red]"
            )
            sys.exit(1)

        key = login(stored_hash, stored_salt)
        if key is not None:
            menu(link, key)
        else:
            console.print(
                "\n[bold red]Too many failed attempts. Access denied.[/bold red]"
            )
            sys.exit(1)

    # Flow for first-time user setup
    else:
        console.print(
            Panel(
                "[bold yellow]Welcome! Initializing new password vault...[/bold yellow]",
                border_style="yellow",
            )
        )
        create_tables(link)
        pw = create_master_passwd()

        if pw is not None:
            hashed_pw = hash_pw(pw)
            salt = derive_salt()
            add_master_pw(link, hashed_pw, salt)

            # Immediate login verification with the generated salt
            key = login(hashed_pw, salt)
            if key is not None:
                menu(link, key)
            else:
                console.print(
                    "\n[bold red]Login failed during setup.[/bold red]"
                )
                sys.exit(1)
        else:
            console.print(
                "\n[bold red]Setup cancelled. Passwords did not match.[/bold red]"
            )
            sys.exit(1)


if __name__ == "__main__":
    main()
