# 🔐 TOTP Authenticator

A simple yet powerful 2FA (Two-Factor Authentication) code generator written in Python.  
It supports secure secret storage, TOTP code generation, QR scanning, auto-lock, tray minimization, and optional GUI or CLI modes.

---

## ✅ Features

- 🔒 **Master password-protected storage**
- 🔐 **TOTP generation** (Time-based One-Time Password)
- 🧠 **Encrypted local secrets** using `cryptography.Fernet`
- 🖼️ **Scan QR codes** from image or webcam
- 🕒 **Auto-refreshing countdown timer**
- ☑️ **Export/Import** encrypted secrets as JSON
- 🧊 **Tray icon + minimize support**
- 💻 Dual-mode: **GUI and CLI interface**

---

## 📦 Installation

1. **Clone the repository:**

```bash
git clone https://github.com/TT5H/totp-authenticator.git
cd totp-authenticator
```

2. **Install dependencies:**

```bash
pip install -r requirements.txt
```

3. **Run the app:**

```bash
python main.py
```

---

## ⚙️ Configuration

Modify `config.json` to switch modes or customize behavior:

```json
{
  "refresh_interval": 30,
  "export_filename": "secrets_export.json",
  "auto_lock_timeout": 300,
  "use_gui": true,
  "enable_qr_scan": true,
  "enable_webcam_scan": true,
  "enable_tray_minimize": true,
  "default_secret_file": "secrets.json"
}
```

- `use_gui`: Launch the graphical interface (set `false` to use CLI)
- `auto_lock_timeout`: Time in seconds before app locks after inactivity
- `refresh_interval`: TOTP refresh cycle (usually 30 seconds)

---

## 🖥 GUI vs CLI

- **GUI mode**: Full-featured UI with QR scanning, tray icon, auto-lock
- **CLI mode**: Lightweight terminal-based experience with TOTP generation, countdown, and secure storage

---

## 🔐 Security Notes

- Secrets are stored locally and encrypted using a key derived from your **master password**
- The password is **never stored in plaintext**
- The encryption key is held only in memory during your session

---

## 🧪 Requirements

```text
pyotp
cryptography
pillow
pyzbar
opencv-python
pystray
```

Install them using:

```bash
pip install -r requirements.txt
```

---

## 📁 Project Structure

```
totp_authenticator/
├── main.py               # Entry point for CLI or GUI launcher
├── gui.py                # GUI interface with Tkinter
├── storage.py            # Secure encrypted local storage
├── totp_generator.py     # TOTP generation logic
├── security_utils.py     # Master password and encryption key handler
├── config.json           # Configuration file
├── requirements.txt      # Required Python packages
└── README.md             # You're here
```

---

## 🚀 Packaging (optional)

To create a standalone `.exe` (no Python required):

```bash
pip install pyinstaller
pyinstaller --onefile --windowed main.py
```

Your app will be generated in the `dist/` folder.

---

## 📃 License

MIT License © 2025 [TT5H](https://github.com/TT5H)
