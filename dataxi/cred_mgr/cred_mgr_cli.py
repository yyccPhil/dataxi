import argparse
from .cred_mgr import CredMgr
import getpass


def main():
    # Create the top-level parser
    parser = argparse.ArgumentParser(description="Dataxi Credential Management CLI tool")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Subcommand to add credentials
    subparsers.add_parser("add", help="Add new credential interactively")

    # Subcommand to list all connection IDs
    subparsers.add_parser("list", aliases=["ls"], help="List all connection IDs")

    # Subcommand to delete a credential
    parser_delete = subparsers.add_parser("delete", aliases=["D"], help="Delete a specific credential")
    parser_delete.add_argument("conn_id", help="Connection ID to delete")

    # Subcommand to load credential(s)
    parser_load = subparsers.add_parser("load", help="Load a specific credential or all credentials")
    group = parser_load.add_mutually_exclusive_group(required=True)
    group.add_argument("-id", "--conn_id", help="Connection ID to load")
    group.add_argument("-a", "--all", action="store_true", help="Load all credentials")
    
    # Subcommand to send the credential securely
    parser_send = subparsers.add_parser("send", help="Send a credential securely")
    group = parser_send.add_mutually_exclusive_group(required=True)
    group.add_argument("-id", "--conn_id", help="Connection ID to send")
    group.add_argument("-s", "--secret", help="Specify the secret to send")
    parser_send.add_argument("--ttl", help="Specify the time-to-live in seconds, default is 3600 seconds")
    parser_send.add_argument("-cfg", "--config", choices=['us', 'eu', 'default'], help="Specify the configuration to use")

    # Subcommand to clean the credential folder
    subparsers.add_parser("clean", help="Delete the credential folder")

    # Subcommand to reset the credential storage file
    subparsers.add_parser("reset", help="Reset the credential storage file")

    args = parser.parse_args()
    cred_mgr = CredMgr()

    # Call the corresponding method based on the subcommand
    if args.command == "add":
        # Interactive mode for adding credentials
        conn_id = input("Enter connection ID (conn_id): ").strip()
        print("\nSelect credential type:")
        print("1. Database")
        print("2. Secret")
        print("3. Token")
        cred_type = input("Enter option (1/2/3): ").strip()

        if cred_type == "1":
            # Database credentials
            
            valid_db_types = ['mysql', 'mssql', 'sql_server', 'clickhouse', 'ch', 'postgresql', 'postgres']
            db_type = input("Enter database type (valid: 'mysql', 'mssql'/'sql_server', 'clickhouse'/'ch', 'postgresql'/'postgres'): ").strip().lower()
            while db_type not in valid_db_types:
                print("Invalid database type. Please enter one of: 'mysql', 'mssql'/'sql_server', 'clickhouse'/'ch', 'postgresql'/'postgres'.")
                db_type = input("Enter valid database type: ").strip().lower()
                
            user = input("Enter username: ").strip()
            password = getpass.getpass("Enter password (hidden): ").strip()
            host = input("Enter host address: ").strip()
            
            port = input("Enter port number: ").strip()
            while not port.isdigit():
                print("Invalid port. Please enter integer.")
                port = input("Enter valid port number: ").strip()
                
            database = input("Enter database name (optional, press Enter to skip): ").strip()
            if database == "":
                database = None
                
            cred_mgr.add_cred(
                conn_id=conn_id,
                user=user,
                password=password,
                db_type=db_type,
                host=host,
                port=int(port),
                database=database
            )
        elif cred_type == "2":
            # Secret credentials
            user = input("Enter username: ").strip()
            password = getpass.getpass("Enter password (hidden): ").strip()
            cred_mgr.add_cred(
                conn_id=conn_id,
                user=user,
                password=password
            )
        elif cred_type == "3":
            # Token credentials
            token = input("Enter token: ").strip()
            cred_mgr.add_cred(
                conn_id=conn_id,
                db_type="token",
                token=token
            )
        else:
            print("Invalid option. Exiting.")
    elif args.command in ("list", "ls"):
        cred_mgr.list_conn_id()
    elif args.command in ("delete", "D"):
        cred_mgr.delete_cred(conn_id=args.conn_id)
    elif args.command == "load":
        cred_mgr.load_cred(conn_id=args.conn_id, all=args.all)
    elif args.command == "clean":
        confirm = input("Are you sure to clean the credential folder? (Warning: This action is irreversible!) (Y/n): ").strip().lower()
        if confirm != "y":
            print("Operation cancelled. Exiting.")
            return
        cred_mgr.clean_cred_folder()
    elif args.command == "reset":
        confirm = input("Are you sure to reset the credential storage file? (Warning: This action is irreversible!) (Y/n): ").strip().lower()
        if confirm != "y":
            print("Operation cancelled. Exiting.")
            return
        cred_mgr.reset_cred()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()