import pyotp
import time

def generate_totp(secret):
    """
    Generate the current TOTP code
    """
    totp = pyotp.TOTP(secret)
    return totp.now()


def get_totp_with_timeleft(secret):
    """
    Return TOTP code along with how many secs are left before it changes
    """
    totp = pyotp.TOTP(secret)
    time_left = totp.interval - (int(time.time()) % totp.interval)
    return totp.now(), time_left
