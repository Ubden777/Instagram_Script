import argparse
from app.db import Session, Account, init_db
from app.encrypt import encrypt_data, decrypt_data
from getpass import getpass

def add_account(session, username, profile_id, proxy):
    password = getpass("Enter password for the account: ")
    encrypted_password = encrypt_data(password)

    new_account = Account(
        username=username,
        password_encrypted=encrypted_password,
        profile_id=profile_id,
        proxy=proxy,
        status='active',
        enabled=True
    )
    session.add(new_account)
    session.commit()
    print(f"Account '{username}' added successfully.")

def update_account(session, username, profile_id=None, proxy=None):
    account = session.query(Account).filter_by(username=username).first()
    if not account:
        print(f"Account '{username}' not found.")
        return

    if profile_id:
        account.profile_id = profile_id
    if proxy:
        account.proxy = proxy

    password = getpass(f"Enter new password for {username} (leave blank to keep current): ")
    if password:
        account.password_encrypted = encrypt_data(password)

    session.commit()
    print(f"Account '{username}' updated successfully.")

def list_accounts(session):
    accounts = session.query(Account).all()
    if not accounts:
        print("No accounts found.")
        return

    for acc in accounts:
        print(f"ID: {acc.id}, Username: {acc.username}, Profile ID: {acc.profile_id}, "
              f"Proxy: {acc.proxy}, Status: {acc.status}, Enabled: {acc.enabled}")

def main():
    parser = argparse.ArgumentParser(description="Manage Instagram accounts.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Add command
    parser_add = subparsers.add_parser("add", help="Add a new account.")
    parser_add.add_argument("--username", required=True, help="Instagram username.")
    parser_add.add_argument("--profile-id", required=True, help="MoreLogin profile ID.")
    parser_add.add_argument("--proxy", required=True, help="Proxy address.")

    # Update command
    parser_update = subparsers.add_parser("update", help="Update an existing account.")
    parser_update.add_argument("--username", required=True, help="Instagram username.")
    parser_update.add_argument("--profile-id", help="New MoreLogin profile ID.")
    parser_update.add_argument("--proxy", help="New proxy address.")

    # List command
    subparsers.add_parser("list", help="List all accounts.")

    # Init DB command
    subparsers.add_parser("initdb", help="Initialize the database.")

    args = parser.parse_args()

    if args.command == "initdb":
        init_db()
        print("Database initialized.")
        return

    session = Session()
    try:
        if args.command == "add":
            add_account(session, args.username, args.profile_id, args.proxy)
        elif args.command == "update":
            update_account(session, args.username, args.profile_id, args.proxy)
        elif args.command == "list":
            list_accounts(session)
    finally:
        session.close()

if __name__ == "__main__":
    main()
