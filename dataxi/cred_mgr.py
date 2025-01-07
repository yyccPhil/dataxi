# File: /dataxi/cred_mgr.py

# Creator: Yuan Yuan (yyccPhil)

# Version:

# 2024.12.11:
#     1. Initial version.
# 2024.12.31:
#     1. Rewrote initialize functions;
#     2. Added list_conn_id().
# 2025.01.07:
#     1. added token type to credentials;
#     2. renamed the file, class and func name to 'cred'.


import os
import json
from pathlib import Path


class CredMgr:
    def __init__(self):
        """Initialize credentials storage path. If it does not exist, create the path."""
        self.config_dir = Path.home() / ".dataxi"    # placing a "." (period) in front of the folder, will hide it in finder
        self.cred_path = self.config_dir / "creds.json"
        self.initialize_cred_path()
    
    def initialize_cred_path(self):
        """Check if the file path exists; if not, create the file and folder."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        if not self.cred_path.exists():
            self.cred_path.write_text("{}")

    def save_cred(self, conn_id: str, user: str=None, password: str=None, db_type: str=None, host: str=None, port: str=None, database: str=None, token: str=None):
        """Save the credential to the local file.

        Args:
            conn_id: the customized connection id of the database.
            db_type: the database source type ('mysql', 'mssql'/'sql_server', 'clickhouse'/'ch').
        """
        if db_type=='token':
            cred_dict = {"token": token}
        elif db_type:
            cred_dict = {"db_type": db_type, "host": host, "port": port, "user": user, "password": password, "database": database}
        else:
            cred_dict = {"user": user, "password": password}
        with open(self.cred_path, "r") as f:
            cred_data = json.load(f)
            
        if conn_id in cred_data:
            print(f"conn_id: '{conn_id}' already exists. If want to overwrite it, please use delete_cred() to remove it first.")
            return None
        
        cred_data[conn_id] = cred_dict
        with open(self.cred_path, "w") as f:
            json.dump(cred_data, f, indent=4)
        
        os.chmod(self.cred_path, 0o600)  # grant the file access
        
        print(f"Added credential: {conn_id}")

    def list_conn_id(self):
        """List all conn_id."""
        with open(self.cred_path, "r") as f:
            cred_data = json.load(f)
            for key in sorted(cred_data.keys()):
                print(key)

    def delete_cred(self, conn_id: str):
        """Delete the specific credential using conn_id from the local credential file."""
        with open(self.cred_path, "r") as f:
            cred_data = json.load(f)
            
        if conn_id not in cred_data:
            print(f"conn_id: '{conn_id}' does not exist.")
            return None
        
        cred_data.pop(conn_id)
        with open(self.cred_path, "w") as f:
            json.dump(cred_data, f, indent=4)
        
        os.chmod(self.cred_path, 0o600)  # grant the file access
        
        print(f"Successfully deleted credential: {conn_id}")

    def load_cred(self, conn_id=None, all=False):
        """Load the credential(s).
        
        Args:
            conn_id: the customized connection id of the database.
            all: flag to load all credentials. If True, will load all credentials.
        """
        with open(self.cred_path, "r") as f:
            cred_data = json.load(f)
            if all:
                print(cred_data)
                return None
            if conn_id in cred_data:
                print(cred_data[conn_id])
            else:
                print(f"conn_id: '{conn_id}' does not exist.")

    def clean_cred_folder(self):
        """Delete the .dataxi folder."""
        config_dir = Path.home() / ".dataxi" 
        if os.path.exists(config_dir):
            import shutil
            shutil.rmtree(config_dir)
            print(f"Folder deleted: {config_dir}")
        else:
            print("Folder does not exist.")

    def reset_cred(self):
        """Reset the credential storage file."""
        self.clean_cred_folder()
        self.initialize_cred_path()
        print("Credential storage file reset.")


def save_cred_env(conn_id: str, db_type: str, host: str, port: str, user: str, password: str, database: str=None):
    """(Beta) Save the credential to the local global env (only for MacOS).

    Args:
        conn_id: the customized connection id of the database.
        db_type: the database source type (mysql, mssql/sql_server, clickhouse/ch).
    """
    # Get Shell value from ENV variable
    current_shell = os.environ.get('SHELL')
    if current_shell.split('/')[-1] == 'zsh':
        env_file_name = ".zshrc"
    elif current_shell.split('/')[-1] == 'bash':
        env_file_name = ".bashrc"
    else:
        print('Not avaiable for the current OS. Please consider using save_cred() to save the credential to local file.')
        return None
    
    export_line = f'export {conn_id}=\'{{"db_type": "{db_type}", "host": "{host}", "port": "{port}", "user": "{user}", "password": "{password}", "database": "{database}"}}\'\n'

    # Get user's .bashrc file path
    env_file_path = Path.home() / env_file_name

    # Check if the same export line is existing
    if env_file_path.exists():
        content = env_file_path.read_text()
        if export_line in content:
            print(f"The export line already exists in the {env_file_name} file.")
        else:
            env_file_path.write_text(content + export_line)
            print(f"Added the export line to the {env_file_name} file.")
    else:
        # If the env file does not exist, create and add the line.
        env_file_path.write_text(export_line)
        print(f"{env_file_name} file does not exist, already created and added the line.")

    # Prompt the user to reload .bashrc
    print("Please run the following command to apply the changes:")
    print(f"source ~/{env_file_name}")
