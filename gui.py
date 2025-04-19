import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import json
import os
import time
import threading
import pyotp
from PIL import Image
from pyzbar.pyzbar import decode
import cv2
import pystray
from pystray import MenuItem as item

from totp_generator import generate_totp
from storage import get_secret, add_secret, export_secrets
from security_utils import verify_master_password

CONFIG_FILE = "config.json"
if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE) as f:
        config = json.load(f)
else:
    config = {
        "refresh_interval": 30,
        "export_filename": "secrets_export.json",
        "auto_lock_timeout": 300,
        "use_gui": True,
        "enable_qr_scan": True
    }

REFRESH_INTERVAL = config.get("refresh_interval", 30)
AUTO_LOCK_TIMEOUT = config.get("auto_lock_timeout", 300)
ENABLE_QR_SCAN = config.get("enable_qr_scan", True)

class TOTPApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🔐 TOTP Authenticator")
        self.root.geometry("400x420")
        self.secret_name = tk.StringVar()
        self.running = False
        self.last_active = time.time()

        if not verify_master_password():
            messagebox.showerror("Access Denied", "Incorrect master password.")
            root.destroy()
            return

        self.build_gui()
        self.root.bind_all("<Any-KeyPress>", self.reset_timer)
        self.root.bind_all("<Any-Button>", self.reset_timer)
        self.root.protocol("WM_DELETE_WINDOW", self.minimize_to_tray)

        self.auto_lock_thread = threading.Thread(target=self.auto_lock)
        self.auto_lock_thread.daemon = True
        self.auto_lock_thread.start()

    def build_gui(self):
        frame = ttk.Frame(self.root, padding=10)
        frame.pack(expand=True, fill="both")

        ttk.Label(frame, text="Select Account:", font=("Segoe UI", 10)).pack(pady=5)
        self.name_menu = ttk.Combobox(frame, textvariable=self.secret_name, font=("Segoe UI", 10))
        self.name_menu['values'] = self.load_secret_names()
        self.name_menu.pack(pady=5)

        self.toggle_button = ttk.Button(frame, text="▶ Start", command=self.toggle)
        self.toggle_button.pack(pady=10)

        self.code_label = ttk.Label(frame, text="TOTP Code: ---", font=("Consolas", 20))
        self.code_label.pack(pady=10)

        self.timer_label = ttk.Label(frame, text="⏳ Time Left: -- s", font=("Segoe UI", 12))
        self.timer_label.pack(pady=5)

        ttk.Separator(frame).pack(fill="x", pady=10)

        ttk.Button(frame, text="🔁 Refresh Secrets", command=self.refresh_secrets).pack(pady=2)
        ttk.Button(frame, text="📤 Export Secrets", command=export_secrets).pack(pady=2)

        if ENABLE_QR_SCAN:
            ttk.Button(frame, text="📷 Scan QR from Image", command=self.scan_qr_image).pack(pady=2)
            ttk.Button(frame, text="🎥 Scan QR from Webcam", command=self.scan_qr_webcam).pack(pady=2)

    def load_secret_names(self):
        if os.path.exists("secrets.json"):
            with open("secrets.json") as f:
                data = json.load(f)
            return list(data.keys())
        return []

    def refresh_secrets(self):
        self.name_menu['values'] = self.load_secret_names()

    def toggle(self):
        if self.running:
            self.running = False
            self.toggle_button.config(text="▶ Start")
        else:
            if not self.secret_name.get():
                messagebox.showwarning("Warning", "Please select a secret.")
                return
            self.running = True
            self.toggle_button.config(text="⏹ Stop")
            threading.Thread(target=self.update_totp).start()

    def update_totp(self):
        while self.running:
            secret = get_secret(self.secret_name.get())
            if secret:
                code = generate_totp(secret)
                time_left = REFRESH_INTERVAL - (int(time.time()) % REFRESH_INTERVAL)
                self.code_label.config(text=f"TOTP Code: {code}")
                self.timer_label.config(text=f"⏳ Time Left: {time_left} s")
            else:
                self.code_label.config(text="TOTP Code: ---")
                self.timer_label.config(text="⏳ Time Left: -- s")
            time.sleep(1)

    def scan_qr_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if not file_path:
            return
        try:
            img = Image.open(file_path)
            decoded = decode(img)
            self.process_qr(decoded)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def scan_qr_webcam(self):
        cap = cv2.VideoCapture(0)
        while True:
            ret, frame = cap.read()
            decoded = decode(frame)
            cv2.imshow("Scan QR - Press Q to exit", frame)
            if decoded:
                self.process_qr(decoded)
                break
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cap.release()
        cv2.destroyAllWindows()

    def process_qr(self, decoded):
        if decoded:
            uri = decoded[0].data.decode()
            if uri.startswith("otpauth://totp/"):
                totp = pyotp.parse_uri(uri)
                name = totp.name
                secret = totp.secret
                add_secret(name, secret)
                messagebox.showinfo("QR Scan", f"Secret '{name}' added successfully.")
                self.refresh_secrets()
            else:
                messagebox.showerror("Error", "Invalid TOTP QR code.")
        else:
            messagebox.showerror("Error", "No QR code found.")

    def reset_timer(self, event=None):
        self.last_active = time.time()

    def auto_lock(self):
        while True:
            if time.time() - self.last_active > AUTO_LOCK_TIMEOUT:
                messagebox.showinfo("Auto Lock", "App locked due to inactivity.")
                self.root.quit()
                break
            time.sleep(5)

    def minimize_to_tray(self):
        self.root.withdraw()
        image = Image.new("RGB", (64, 64), "black")
        icon = pystray.Icon("totp_tray", image, "TOTP Authenticator", menu=pystray.Menu(
            item("Restore", self.restore),
            item("Exit", self.exit_app)
        ))
        threading.Thread(target=icon.run).start()

    def restore(self):
        self.root.after(0, self.root.deiconify)

    def exit_app(self):
        self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = TOTPApp(root)
    root.mainloop()