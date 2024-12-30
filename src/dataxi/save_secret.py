# File: ./src/dataxi/save_secret.py

# Creator: Yuan Yuan (yyccPhil)

# Version:

# 2024.12.11:
#     1. Initial version.


import os
import json
from pathlib import Path


class SaveSecret:
    def __init__(self):
        """Initiate secrets storage path. If it does not exist, create the path."""
        config_dir = Path.home() / ".dataxi"    # placing a "." (period) in front of the folder, will hide it in finder
        config_dir.mkdir(parents=True, exist_ok=True)

        self.secret_path = config_dir / "secrets.json"
        if not self.secret_path.exists():
            self.secret_path.write_text("{}")
    
    def get_secret_path(self):
        """Get the secrets storage path."""
        return self.secret_path

    def save_secret(self, conn_id: str, user: str, password: str, db_type: str=None, host: str=None, port: str=None, database: str=None):
        """Save the secret to the local file.

        Args:
            conn_id: the customized connection id of the database.
            db_type: the database source type (mysql, mssql/sql_server, clickhouse/ch).
        """
        if db_type:
            secret_dict = {"db_type": db_type, "host": host, "port": port, "user": user, "password": password, "database": database}
        else:
            secret_dict = {"user": user, "password": password}
        with open(self.secret_path, "r") as f:
            secret_data = json.load(f)
            
        if conn_id in secret_data:
            print(f"conn_id: '{conn_id}' already exists. If want to overwrite it, please use delete_secret() to remove it first.")
            return None
        
        secret_data[conn_id] = secret_dict
        with open(self.secret_path, "w") as f:
            json.dump(secret_data, f, indent=4)
        
        os.chmod(self.secret_path, 0o600)  # grant the file access
        
        print(f"Added secret: {conn_id}")

    def delete_secret(self, conn_id: str):
        """Delete the specific secret from the local secret file."""
        with open(self.secret_path, "r") as f:
            secret_data = json.load(f)
            
        if conn_id not in secret_data:
            print(f"conn_id: '{conn_id}' does not exist.")
            return None
        
        secret_data.pop(conn_id)
        with open(self.secret_path, "w") as f:
            json.dump(secret_data, f, indent=4)
        
        os.chmod(self.secret_path, 0o600)  # grant the file access
        
        print(f"Successfully deleted secret: {conn_id}")

    def load_secrets(self, conn_id=None, all=False):
        """Load the secrets.
        
        Args:
            conn_id: the customized connection id of the database.
            all: flag to load all secrets. If True, will load all secrets.
        """
        with open(self.secret_path, "r") as f:
            secret_data = json.load(f)
            if all:
                return secret_data
            if conn_id in secret_data:
                return secret_data[conn_id]
            else:
                print(f"conn_id: '{conn_id}' does not exist.")

    def clean_secret_folder(self):
        """Delete the .dataxi folder."""
        config_dir = Path.home() / ".dataxi" 
        if os.path.exists(config_dir):
            import shutil
            shutil.rmtree(config_dir)
            print(f"Folder deleted: {config_dir}")
        else:
            print("Folder does not exist.")

    def reset_secret(self):
        """Reset the secret file."""
        self.clean_secret_folder()
        self.get_secret_path()
        print("Secrets file reset.")


def save_secret_env(conn_id: str, db_type: str, host: str, port: str, user: str, password: str, database: str=None):
    """Save the secret to the local global env (only for MacOS).

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
        print('Not avaiable for the current OS. Please consider using save_secret() to save the secrets to local file.')
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
