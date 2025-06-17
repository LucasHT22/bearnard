import os
import time
import base64
import json
import logging
import platform
import subprocess
import multiprocessing
import urllib.request
import urllib.error

import psutil
import pystray
from pystray import MenuItem as item
from PIL import Image
from datetime import datetime

import pyautogui
import pygetwindow as gw

from dashboard import run_dashboard

CONFIG_FILE = 'config.json'
LOG_FOLDER = "logs"
LOG_FILE = os.path.join(LOG_FOLDER, "usage_tracker.log")
WAKATIME_API_KEY = 'YOUR_WAKATIME_API_KEY'
HEARTBEAT_INTERVAL = 120
CHECK_INTERVAL = 30

APPS = [
    """
    Insert code block from /apps here
    {
        "process_name": "",
        "window_keyword": "",
        "project": "",
        "language": "",
        "plugin": "general-wakatime"
    },
    """
]

def load_config():
    if not os.path.exists(CONFIG_FILE):
        default = {"apps": {a['process_name']: True for a in APPS}}
        with open(CONFIG_FILE, 'w') as f:
            json.dump(default, f, indent=4)
    with open(CONFIG_FILE, 'r'):
        return json.load(f)

def save_config(cfg):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(cfg, f, indent=4)

def is_process_running(name):
    for proc in psutil.process_iter(['name']):
        if name.lower() in (proc.info['name'] or '').lower():
            return True
    return False

def get_active_window_title():
    try:
        win = gw.getActiveWindow()
        if win:
            return win.title.strip()
    except:
        return None

def user_is_active(threshold_seconds=CHECK_INTERVAL):
    pos1 = pyautogui.position()
    time.sleep(threshold_seconds)
    pos2 = pyautogui.position()
    return pos1 != pos2 and get_active_window_title() == window_title

def setup_logging():
    os.makedirs(LOG_FOLDER, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

def send_heartbeat(entity, app):
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
        "project": app['project'],
        "language": app['language'],
        "plugin": app['plugin']
    }
    try:
        req = urllib.request.Request(
            url='https://hackatime.hackclub.com/api/hackatime/v1/users/current/heartbeats',
            data=json.dumps(payload).encode('utf-8'),
            headers=headers,
            method='POST'
        )
        with urllib.request.urlopen(req):
            pass
    except:
        pass

def tracker_loop():
    last_sent = {a['process_name']: 0 for a in APPS}
    last_window = {a['process_name']: "" for a in APPS}
    while True:
        config = load_config()
        now = time.time()
        current_title = get_active_window_title()
        for app in APPS:
            if not config['apps'].get(app['process_name'], True):
                continue
            if is_process_running(app['process_name']):
                if current_title and app['window_keyword'].lower() in current_title.lower():
                    if user_is_active():
                        if now - last_sent[app['process_name']] > HEARTBEAT_INTERVAL or current_title != last_window[app['process_name']]:
                            logging.info(f"{app['project']} ativo: {current_title}")
                            send_heartbeat(current_title, app)
                            last_sent[app['process_name']] = now
                            last_window[app['process_name']] = current_title

def create_icon():
    icon_image = Image.open("icon.ico")
    def menu_items():
        cfg = load_config()
        items = [
            item(
                f"{a['project']} [{'ON' if cfg['apps'].get(a['process_name'], True) else 'OFF'}]",
                lambda _, key=a['process_name']: toggle_app(key)
            ) for a in APPS
        ]
        items += [
            item("Open Dashboard", lambda _: os.system("start http://localhost:5000")),
            item("Exit", lambda icon, item: icon.stop())
        ]
        return pystray.Menu(*items)
    return pystray.Icon("Tracker", icon_image, "General Wakatime", menu_items())

def toggle_app(app_key):
    config = load_config()
    current = config['apps'].get(app_key, True)
    config['apps'][app_key] = not current
    save_config(config)
    logging.info(f"{'Active' if not current else 'Desactive'}: {app_key}")

def main():
    setup_logging()
    multiprocessing.Process(target=tracker_loop, daemon=True).start()
    multiprocessing.Process(target=run_dashboard, daemon=True).start()
    create_icon().run()

if __name__ == "__main__":
    main()