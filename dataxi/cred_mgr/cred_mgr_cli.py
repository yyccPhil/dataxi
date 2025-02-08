import argparse
from .cred_mgr import CredMgr


def main():
    # Create the top-level parser
    parser = argparse.ArgumentParser(description="Dataxi Credential Management CLI tool")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Subcommand to add credentials
    parser_add = subparsers.add_parser("add", help="Add new credential interactively")
    parser_add.add_argument("conn_id", help="Connection ID to add")

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
        cred_mgr.add_cred(conn_id=args.conn_id)
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