import json
import os
from cryptography.fernet import Fernet
from security_utils import get_master_key

# Load config settings
CONFIG_FILE = "config.json"
if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE) as f:
        config = json.load(f)
else:
    config = {
        "default_secret_file": "secrets.json",
        "export_filename": "secrets_export.json"
    }

STORAGE_FILE = config.get("default_secret_file", "secrets.json")
EXPORT_FILE = config.get("export_filename", "secrets_export.json")


def _get_fernet():
    key = get_master_key()  # This ensures encryption is tied to master password
    return Fernet(key)


def add_secret(name, secret):
    f = _get_fernet()
    if os.path.exists(STORAGE_FILE):
        with open(STORAGE_FILE, "r") as f_in:
            try:
                data = json.load(f_in)
            except json.JSONDecodeError:
                data = {}
    else:
        data = {}
    
    data[name] = f.encrypt(secret.encode()).decode()
    
    with open(STORAGE_FILE, "w") as f_out:
        json.dump(data, f_out, indent=2)


def get_secret(name):
    f = _get_fernet()
    if not os.path.exists(STORAGE_FILE):
        return None
    with open(STORAGE_FILE, "r") as f_in:
        data = json.load(f_in)
    encrypted = data.get(name)
    if not encrypted:
        return None
    return f.decrypt(encrypted.encode()).decode()


def export_secrets():
    if not os.path.exists(STORAGE_FILE):
        print("❌ No secrets to export.")
        return
    with open(STORAGE_FILE, "r") as f:
        data = json.load(f)
    with open(EXPORT_FILE, "w") as f_out:
        json.dump(data, f_out, indent=2)
    print(f"✅ Secrets exported to {EXPORT_FILE}")


def import_secrets():
    if not os.path.exists(EXPORT_FILE):
        print("❌ No export file found.")
        return
    with open(EXPORT_FILE, "r") as f:
        try:
            new_data = json.load(f)
        except json.JSONDecodeError:
            print("❌ Invalid export file.")
            return

    if os.path.exists(STORAGE_FILE):
        with open(STORAGE_FILE, "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = {}
    else:
        data = {}

    data.update(new_data)

    with open(STORAGE_FILE, "w") as f:
        json.dump(data, f, indent=2)
    print("✅ Secrets imported successfully.")
