import urllib.request
import urllib.parse
import json
from pathlib import Path
import configparser
from .cred_mgr import CredMgr
from pathlib import Path


class CredSender:
    def __init__(self):
        """Initialize config file path. If it does not exist, create the path."""
        self.config = configparser.ConfigParser()
        self.config_dir = Path.home() / ".dataxi"    # placing a "." (period) in front of the folder, will hide it in finder
        self.cred_path = self.config_dir / "config.ini"
        self.initialize_config()
    
    def initialize_config(self):
        """Check if the config file exists; if not, create the file and folder."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config.read(self.cred_path)

        # Add the [sender] section if it doesn't already exist
        if 'sender' not in self.config:
            self.config.add_section('sender')

        # Set secret_send_region to 'us'
        self.config.set('sender', 'secret_send_region', 'us')

        # Write the configuration back to config.ini
        with open(self.cred_path, 'w') as configfile:
            self.config.write(configfile)

    def set_region_config(self, region):
        """Set the configuration to specific region."""
        self.config.read(self.cred_path)
        self.config.set('sender', 'secret_send_region', region)
        with open(self.cred_path, 'w') as configfile:
            self.config.write(configfile)
            
    def generate_secret_url(self, secret_text, passphrase, ttl):
        """Generate the secret URL.

        Args:
            secret_text (str): The secret text to be shared.
            passphrase (str): Optional passphrase.
            ttl (int): Time-to-live (TTL) in seconds.
        """
        self.config.read(self.cred_path)
        region = self.config.get('sender', 'secret_send_region')

        # powered by https://onetimesecret.com/
        url = f"https://{region}.onetimesecret.com/api/v1/share"
        
        if passphrase:
            data = {
                "secret": secret_text,  # The secret to be shared
                "ttl": str(ttl),    # Time-to-live (TTL) in seconds
                "passphrase": passphrase   # Optional passphrase
            }
        else:    
            data = {
                "secret": secret_text,  # The secret to be shared
                "ttl": str(ttl)    # Time-to-live (TTL) in seconds
            }
        
        # Encode data for the POST request
        encoded_data = urllib.parse.urlencode(data).encode("utf-8")

        # Send a POST request
        req = urllib.request.Request(url, data=encoded_data, method="POST")
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode("utf-8"))  # Parse JSON response
            print(f"Secret URL: https://{region}.onetimesecret.com/secret/{result['secret_key']}")

    
    def send_secret(self, secret, passphrase=None, ttl=None):
        """Send the secret text securely and return the secret URL."""
        if ttl is None:
            ttl = 3600
        self.generate_secret_url(secret, passphrase, ttl)
        
    def send_conn_id(self, conn_id, passphrase=None, ttl=None):
        """Send the conn_id corresponding credential securely and return the secret URL."""
        # Initialize CredMgr to make sure the credential file exists
        CredMgr()
        config_dir = Path.home() / ".dataxi"
        cred_path = config_dir / "creds.json"
        with open(cred_path, "r") as f:
            cred_data = json.load(f)
            if conn_id in cred_data:
                cred_dict = cred_data[conn_id]
                print(cred_dict)
            else:
                print(f"conn_id: '{conn_id}' does not exist.")
                return

        secret_text = "\n".join(f"{key}: {value}" for key, value in cred_dict.items())
        secret_text += f'''\n\nOriginal JSON:\n"{conn_id}": {json.dumps(cred_dict)}'''
        
        if ttl is None:
            ttl = 3600
        self.generate_secret_url(secret_text, passphrase, ttl)
