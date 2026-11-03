from .auth import *
from .crypto import *
from .database import *
import os
import sys
import questionary
import pyfiglet
from rich.console import Console
from rich.table import Table
from rich.align import Align
from rich.text import Text

console = Console()

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def display_header():
    ascii_art = pyfiglet.figlet_format("SUB ROSA")
    
    # Center and display
    console.print(Align.center(Text(ascii_art, style="magenta1")))
    console.print(Align.center(Text("Forget the master password, and you are done for\n", style="plum1")))

def menu(link, key):
        while True:
            clear_screen()
            display_header()
            
            choice = questionary.select(
                "Select any one option",
                choices = [
                    "1. Add Entry", 
                    "2. List Entries",
                    "3. Edit Password",
                    "4. Fetch Password",
                    "5. Update Master Password",
                    "6. Delete Entry",
                    "7. Exit"
                    ]
                ).ask()
            
            if choice is None or "Exit" in choice:
                console.print("\n[green_yellow]Exiting vault. Forget the master password and you are done for[/green_yellow]")
                sys.exit()

            elif "Add Entry" in choice:
                console.print("\n[plum1]--- Add New Credentials ---[/plum1]")
                website = questionary.text("Website / Service name:").ask()
            
                if not website or not website.strip():
                    console.print("\n[bold red]✗ Input cancelled or empty.[/bold red]")
                #duplicate check
                elif get_vault_entries(link, website):
                    console.print(
                        f"\n[red]An entry for '{website}' already exists. "
                        "Use Edit Password to change it.[/red]"
                    )
            
                else:
                    username = questionary.text("Username / Email:").ask()
                    pw = questionary.password("Password:").ask()
            
                    if username and pw:
                        ciphertext = encrypt(pw, key)
                        add_vault_entry(link, website, username, ciphertext)
                        console.print(f"\n[bold green]✓ Entry for '{website}' saved![/bold green]")
                    else:
                        console.print("\n[bold red]✗ Input cancelled or empty.[/bold red]")
            
                questionary.press_any_key_to_continue().ask()            

            elif "List Entries" in choice:
                console.print("\n[plum1]--- List Entries ---[/plum1]")
                table = Table(title="All entries", border_style="dim")
                table.add_column("Website", style="plum1")
                table.add_column("Username", style="green_yellow")
                entries = list_entries(link)
                for entry in entries:
                    table.add_row(entry[0], entry[1])
                console.print(table)
                questionary.press_any_key_to_continue().ask()
            
            elif "Edit Password" in choice:
                console.print("\n[plum1]--- Edit Password ---[/plum1]")
                website = questionary.text("Enter website name to update:").ask()

                if website:
                    if get_vault_entries(link, website) is None:
                       console.print(f"\n[bold red]✗ No entry found for '{website}'.[/bold red]") 
                    else:
                        pw = questionary.password("Enter new password:").ask()
                        if pw:
                            ciphertext = encrypt(pw, key)
                            update_entry(link, website, ciphertext)
                            console.print(
                                f"\n[bold green]✓ Password for '{website}' updated successfully![/bold green]"
                            )

                questionary.press_any_key_to_continue().ask()

            elif "Fetch Password" in choice:
                console.print("\n[plum1]--- Fetch Credentials ---[/plum1]")
                website = questionary.text("Enter website name:").ask()

                if website:
                    entry = get_vault_entries(link, website)
                    if entry:
                        #direct unpacking since fetchone() returns a single tuple
                        web, uname, pw_cipher = entry

                        table = Table(title=f"Results for '{website}'", border_style="dim")
                        table.add_column("Website", style="plum1")
                        table.add_column("Username", style="green_yellow")
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
                console.print("\n[plum1]--- Update Master Password ---[/plum1]")
                stored_hash, stored_salt, vault_key_encryp = get_master_auth(link)

                #re-authenticate before allowing master password change
                
                console.print("\n[plum1]Enter current password[/plum1]")
                k = login(stored_hash, stored_salt, vault_key_encryp)
                if k is not None:
                    new_mp = create_master_passwd()
                    if new_mp:
                        hashed_pw = hash_pw(new_mp)
                        new_salt = derive_salt()
                        wrapping_key = derive_key(new_mp, new_salt)
                        new_vault_key_encryp = encrypt(k.decode('utf-8'), wrapping_key)
                        add_master_pw(link, hashed_pw, new_salt, new_vault_key_encryp)
                        console.print(
                            "\n[bold green]✓ Master Password updated!\nPlease restart the app.[/bold green]"
                        )
                        sys.exit(0)
                    else:
                        console.print("\n[bold red]✗Password is empty, or they don't match[/bold red]")
                else:
                    console.print(
                        "\n[bold red]✗ Verification failed.\nMaster password change aborted.[/bold red]"
                    )

                questionary.press_any_key_to_continue().ask()

            elif "Delete Entry" in choice:
                console.print("\n[plum1]--- Delete Entry ---[/plum1]")
                website = questionary.text("Enter website name to delete:").ask()

                if website:
                    if get_vault_entries(link, website) is None:
                        console.print(f"\n[bold red]✗ No entry found for '{website}'.[/bold red]")
                    else:
                        sure = questionary.confirm(f"Permanently delete '{website}'? This cannot be undone.",
                                        default=False,
                                    ).ask()

                        if sure:
                            delete_entry(link, website)
                            console.print(f"\n[bold green]✓ '{website}' deleted.[/bold green]")
                        else:
                            console.print("\n[green_yellow]Cancelled. Nothing was deleted.[/green_yellow]")
                questionary.press_any_key_to_continue().ask()
def main():
    clear_screen()
    display_header()
    link = create_db_connection()

    # flow for returning user with a master password configured
    if master_pw_exists(link):
        # extract the stored hash of mpw and the salt to generate encryption key
        stored_hash, stored_salt, vault_key_encryp = get_master_auth(link)
        if not stored_hash or not stored_salt or not vault_key_encryp:
            console.print(
                "[bold red]Error loading master password from database.[/bold red]"
            )
            sys.exit(1)

        #user log in 
        vault_key = login(stored_hash, stored_salt, vault_key_encryp)
        if vault_key is not None:
            menu(link, vault_key)
        else:
            console.print(
                "\n[bold red]Login cancelled or too many failed attempts. Access denied.[/bold red]"
            )
            sys.exit(1)

    # flow for first-time user setup
    else:
        console.print("[green_yellow]Welcome new user! Set up your vault[/green_yellow]")
        create_tables(link)
        # creation of mpw
        pw = create_master_passwd()

        if pw is not None:
            # (hash + salt) the mpw -> derive and salt for unique key -> store  
            hashed_pw = hash_pw(pw)
            salt = derive_salt()
            vault_key = gen_vault_key()

            wrapping_key = derive_key(pw, salt)
            vault_key_encryp = encrypt(vault_key.decode('utf-8'), wrapping_key)

            add_master_pw(link, hashed_pw, salt, vault_key_encryp)

            menu(link, vault_key)

        else:
            console.print("\n[bold red]Passwords don't match or it's empty[/bold red]")
def run():
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[red]How dare you interrupt me[/red]\n")
        sys.exit(0)

if __name__ == "__main__":
    run()
