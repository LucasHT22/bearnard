import time
import base64
import urllib.request
import urllib.error
import json
import psutil
import platform
import subprocess
import os
from datetime import datetime

try:
    import pyautogui
except ImportError:
    pyautogui = None

WAKATIME_API_KEY = ''
HEARTBEAT_INTERVAL = 120  # seconds
CHECK_INTERVAL = 30       # seconds

APPS = [
    {
        "process_name": "godot-runner",  # Example: VS Code
        "window_keyword": "Pixelorama",
        "project": "Pixelroma",
        "language": "Pixel-art",
        "plugin": "general-wakatime"
    },
    # Add more tracked apps here
]

def is_process_running(name):
    for proc in psutil.process_iter(['name']):
        if name.lower() in (proc.info['name'] or "").lower():
            return True
    return False

def get_active_window_title():
    system = platform.system()
    session_type = os.environ.get("XDG_SESSION_TYPE", "").lower()

    try:
        if system in ["Windows", "Darwin"]:
            import pygetwindow as gw
            win = gw.getActiveWindow()
            if win:
                return win.title.strip()

        elif system == "Linux":
            if session_type == "x11":
                return subprocess.check_output(
                    ["xdotool", "getactivewindow", "getwindowname"]
                ).decode().strip()

            elif session_type == "wayland":
                # KDE Plasma Wayland: D-Bus calls may block compositor or prompt user
                # Safer fallback: just return None or a placeholder
                print("[WARN] Window title detection is limited on KDE Wayland. Falling back to process-only detection.")
                return None
    except Exception as e:
        print(f"[WARN] D-Bus Wayland error: {e}")
    return None


def user_is_active(window_title=None, threshold_seconds=CHECK_INTERVAL):
    session_type = os.environ.get("XDG_SESSION_TYPE", "").lower()

    if platform.system() == "Linux" and session_type == "wayland":
        # Under Wayland, just check if the window stayed focused
        time.sleep(threshold_seconds)
        return get_active_window_title() == window_title

    elif pyautogui:
        try:
            pos1 = pyautogui.position()
            time.sleep(threshold_seconds)
            pos2 = pyautogui.position()
            return pos1 != pos2 and get_active_window_title() == window_title
        except Exception as e:
            print(f"[WARN] pyautogui failed: {e}")
            return False

    else:
        # Fallback if pyautogui is missing
        time.sleep(threshold_seconds)
        return get_active_window_title() == window_title

def save_heartbeat_local(payload):
    with open("heartbeats.json", "a", encoding='utf-8') as f:
        json.dump(payload, f)
        f.write("\n")

def send_heartbeat(entity, app_config):
    encoded_key = base64.b64encode(WAKATIME_API_KEY.encode()).decode()
    headers = {
        "Authorization": f"Basic {encoded_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "time": datetime.utcnow().timestamp(),
        "entity": entity,
        "type": "app",
        "category": "coding",
        "is_write": False,
        "project": app_config['project'],
        "language": app_config['language'],
        "plugin": app_config['plugin']
    }

    req = urllib.request.Request(
        url='https://hackatime.hackclub.com/api/hackatime/v1/users/current/heartbeats',
        data=json.dumps(payload).encode('utf-8'),
        headers=headers,
        method='POST'
    )

    try:
        with urllib.request.urlopen(req) as response:
            print(f"[{datetime.now()}] Heartbeat sent for '{entity}' -> {app_config['project']} ({response.status})")
            save_heartbeat_local(payload)
    except urllib.error.HTTPError as e:
        print(f"[{datetime.now()}] HTTP error: {e.code} - {e.reason}")
    except urllib.error.URLError as e:
        print(f"[{datetime.now()}] Network error: {e.reason}")

def main():
    last_sent = {app['process_name']: 0 for app in APPS}
    last_window = {app['process_name']: "" for app in APPS}

    while True:
        now = time.time()
        current_title = get_active_window_title()

        for app in APPS:
            if is_process_running(app['process_name']):
                # On KDE Wayland, current_title may be None
                if current_title is None or (current_title and app['window_keyword'].lower() in current_title.lower()):
                    if user_is_active(window_title=current_title):
                        if now - last_sent[app['process_name']] > HEARTBEAT_INTERVAL or current_title != last_window[app['process_name']]:
                            send_heartbeat(current_title or app['process_name'], app)
                            last_sent[app['process_name']] = now
                            last_window[app['process_name']] = current_title or ""

if __name__ == "__main__":
    main()
