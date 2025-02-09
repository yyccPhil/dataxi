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
    load_group = parser_load.add_mutually_exclusive_group(required=True)
    load_group.add_argument("-id", "--conn_id", help="Connection ID to load")
    load_group.add_argument("-a", "--all", action="store_true", help="Load all credentials")
    
    # Subcommand to generate a new password
    parser_gen = subparsers.add_parser("gen", help="Generate a new password")
    parser_gen.add_argument("-len", "--length", default=12, help="Password length, default is 12 characters, from 6 to 50 characters", type=int)
    parser_gen.add_argument("-up", "--uppercase", action="store_false", help="Exclude uppercase characters")
    parser_gen.add_argument("-low", "--lowercase", action="store_false", help="Exclude lowercase characters")
    parser_gen.add_argument("-d", "--digit", action="store_false", help="Exclude digits")
    parser_gen.add_argument("-sym", "--symbol", action="store_false", help="Exclude symbols")
    parser_gen.add_argument("-s", "--special", help="Exclude customized special characters")
    parser_gen.add_argument("-a", "--ambiguous", action="store_true", help="Exclude ambiguous characters")
    
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
    elif args.command == "gen":
        cred_mgr.generate_password(length=args.length,
                                    include_uppercase=args.uppercase,
                                    include_lowercase=args.lowercase,
                                    include_digits=args.digit,
                                    include_symbols=args.symbol,
                                    exclude_chars=args.special,
                                    avoid_ambiguous=args.ambiguous)
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