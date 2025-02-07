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
# 2025.02.05:
#     1. renamed the function from 'save_cred' to 'add_cred'.
# 2025.02.07:
#     1. added dict_to_table() and used it in load_cred() when loading all credentials.


import os
import json
from pathlib import Path


def dict_to_table(data: dict) -> str:
    """
    Converts a dictionary to a table formatted with Unicode borders.
    
    Args:
        data: the input dictionary should have keys (as connection IDs) and values (as credential dictionaries).
    Example input:
      {
          "3": {"token": "12312"},
          "123": {"db_type": "ch", "host": "g", "port": 123}
      }
      
    The output is a string representing a table with two columns:
      - 'conn_id'
      - 'credential'
      
    Each credential is converted into a JSON string.
    """
    # Define table header and collect all rows (each row is a list of cell strings)
    header = ["conn_id", "credential (passwords can only be seen when loading the specific conn_id)"]
    rows = []
    for conn_id, cred in data.items():
        hidden_cred = cred.copy()
        if "password" in hidden_cred and hidden_cred["password"]:
            hidden_cred["password"] = "*" * len(hidden_cred["password"])
        cred_str = json.dumps(hidden_cred, ensure_ascii=False)
        rows.append([str(conn_id), cred_str])
    
    # Compute the maximum width for each column (including header and all cell contents)
    col_widths = [len(header[i]) for i in range(len(header))]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(cell))
    
    # Build the top border using Unicode characters
    top_border = "┌" + "┬".join("─" * (w + 2) for w in col_widths) + "┐"
    # Build the header row (centered text)
    header_row = "│" + "│".join(" " + header[i].center(col_widths[i]) + " " for i in range(len(header))) + "│"
    # Build the separator row
    separator = "├" + "┼".join("─" * (w + 2) for w in col_widths) + "┤"
    # Build each data row (left-aligned)
    data_rows = []
    for row in rows:
        data_row = "│" + "│".join(" " + row[i].ljust(col_widths[i]) + " " for i in range(len(row))) + "│"
        data_rows.append(data_row)
    # Build the bottom border
    bottom_border = "└" + "┴".join("─" * (w + 2) for w in col_widths) + "┘"
    
    # Concatenate all parts into the final table string
    table = "\n".join([top_border, header_row, separator] + data_rows + [bottom_border])
    return table


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

    def add_cred(self, conn_id: str, user: str=None, password: str=None, db_type: str=None, host: str=None, port: str=None, database: str=None, token: str=None):
        """Save the credential to the local file.

        Args:
            conn_id: the customized connection id of the database.
            db_type: the database source type ('mysql', 'mssql'/'sql_server', 'clickhouse'/'ch', 'postgresql'/'postgres').
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
                print(dict_to_table(cred_data))
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
        # else:
        #     print("Folder does not exist.")

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
