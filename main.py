"""
Main entry point
"""
import json
import time
import sys
import os
import signal
import subprocess

from totp_generator import generate_totp
from storage import add_secret, get_secret, export_secrets, import_secrets
from security_utils import verify_master_password

# Load config
CONFIG_FILE = "config.json"
if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE) as f:
        config = json.load(f)
else:
    config = {
        "refresh_interval": 30,
        "export_filename": "secrets_export.json",
        "auto_lock_timeout": 300,
        "use_gui": False,
        "enable_qr_scan": True
    }

REFRESH_INTERVAL = config.get("refresh_interval", 30)
LOG_FILE = "error.log"

def graceful_exit(signum, frame):
    print("\\n👋 Exiting gracefully.")
    sys.exit(0)

signal.signal(signal.SIGINT, graceful_exit)

def launch_gui():
    if not os.path.exists("gui.py"):
        print("❌ GUI file not found. Falling back to CLI mode.")
        cli_mode()
        return
    try:
        subprocess.run([sys.executable, "gui.py"])
    except Exception as e:
        with open(LOG_FILE, "a") as log:
            log.write(f"[GUI Error] {e}\\n")
        print("⚠️ Failed to launch GUI. See error.log.")
        cli_mode()

def cli_mode():
    print("Welcome to 🔐 TOTP Authenticator (Terminal Mode)")

    if not verify_master_password():
        print("Access Denied.")
        return

    while True:
        print("\\n1. Add new secret")
        print("2. Generate TOTP with countdown")
        print("3. Export secrets")
        print("4. Import secrets")
        print("5. Exit")

        choice = input("Select an option: ")

        if choice == '1':
            name = input("Enter name for the secret: ")
            secret = input("Enter base32-encoded secret: ")
            add_secret(name, secret)
            print(f"✅ Secret for '{name}' saved.")
        elif choice == '2':
            name = input("Enter name for the secret: ")
            secret = get_secret(name)
            if secret:
                for i in range(REFRESH_INTERVAL, 0, -1):
                    code = generate_totp(secret)
                    print(f"TOTP for {name}: {code} (valid for {i}s)", end="\\r")
                    time.sleep(1)
                print()
            else:
                print("No secret found with that name.")
        elif choice == '3':
            export_secrets()
        elif choice == '4':
            import_secrets()
        elif choice == '5':
            print("👋 Exiting... Bye!")
            break
        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    if config.get("use_gui", False):
        launch_gui()
    else:
        cli_mode()