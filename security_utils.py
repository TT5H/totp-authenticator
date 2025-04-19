import os
import hashlib
from getpass import getpass
from cryptography.fernet import Fernet
import base64

PASS_FILE = "master.pass"
_cached_key = None  # Stored in memory

def _hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def set_master_password():
    password = getpass("Enter a new master password: ")
    confirm = getpass("Confirm password: ")
    if password != confirm:
        print("❌ Passwords do not match.")
        return
    hashed = _hash_password(password)
    with open(PASS_FILE, "w") as f:
        f.write(hashed)
    print("✅ Master password set.")

def verify_master_password():
    global _cached_key
    if not os.path.exists(PASS_FILE):
        print("No master password set. You must create one.")
        set_master_password()
        return True
    stored_hash = open(PASS_FILE).read()
    password = getpass("Enter master password: ")
    if _hash_password(password) == stored_hash:
        # Only cache the key once upon successful auth
        key_hash = hashlib.sha256(password.encode()).digest()
        _cached_key = base64.urlsafe_b64encode(key_hash[:32])
        return True
    return False

def get_master_key():
    global _cached_key
    if _cached_key is None:
        raise Exception("Master password not verified. Call verify_master_password() first.")
    return _cached_key
