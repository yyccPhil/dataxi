import argparse
from .cred_mgr import CredMgr
from .cred_sender import CredSender


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
    
    # Subcommand to send the credential securely
    parser_send = subparsers.add_parser("send", help="Send a credential securely")
    send_group = parser_send.add_mutually_exclusive_group(required=True)
    send_group.add_argument("-id", "--conn_id", help="Connection ID to send")
    send_group.add_argument("-s", "--secret", help="Enter the secret text to send")
    send_group.add_argument("-cfg", "--config", choices=['us', 'eu', 'default'], help="Specify the configuration to use")
    parser_send.add_argument("-p", "--passphrase", help="Optional passphrase to secure the secret")
    parser_send.add_argument("-t", "--ttl", help="Specify the time-to-live in seconds, default is 3600 seconds", type=int)
    
    # Subcommand to reset the credential storage file
    subparsers.add_parser("reset", help="Reset the credential storage file")
    
    # Subcommand to clean the credential folder
    subparsers.add_parser("clean", help="Delete the credential folder")
    
    # Subcommand to get the credential storage path
    subparsers.add_parser("path", help="Get the credential storage path")

    args = parser.parse_args()
    cred_mgr = CredMgr()

    # Call the corresponding method based on the subcommand
    if args.command == "path":
        cred_mgr.get_cred_path()
    elif args.command == "add":
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
    elif args.command == "send":
        if (args.config and args.ttl) or (args.config and args.passphrase):
            parser.error("The --ttl and --passphrase options are only available when sending a secret.")
        cred_sender = CredSender()
        if args.config:
            if args.config in ("us", "default"):
                cred_sender.set_region_config("us")
            elif args.config == "eu":
                cred_sender.set_region_config("eu")
        elif args.conn_id:
            cred_sender.send_conn_id(conn_id=args.conn_id, passphrase=args.passphrase, ttl=args.ttl)
        else:
            cred_sender.send_secret(secret=args.secret, passphrase=args.passphrase, ttl=args.ttl)
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