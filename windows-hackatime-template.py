import time
import base64
import urllib.request
import urllib.error
import json
import psutil
from datetime import datetime
import pygetwindow as gw
import pyautogui

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

def is_process_running(name):
    for proc in psutil.process_iter(['name']):
        if name.lower() in (proc.info['name'] or "").lower():
            return True
    return False

def get_active_window_title():
    try:
        win = gw.getActiveWindow()
        if win:
            return win.title.strip()
    except:
        pass
    return None

def user_is_active(threshold_seconds=CHECK_INTERVAL):
    pos1 = pyautogui.position()
    time.sleep(threshold_seconds)
    pos2 = pyautogui.position()
    return pos1 != pos2 and get_active_window_title() == window_title

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
            print(f"[{datetime.now()}] Heartbeat: {entity} -> {app_config['project']} ({response.status})")
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
                if current_title and app['window_keyword'].lower() in current_title.lower():
                    if user_is_active():
                        if now - last_sent[app['process_name']] > HEARTBEAT_INTERVAL or current_title != last_window[app['process_name']]:
                            send_heartbeat(current_title, app)
                            last_sent[app['process_name']] = now
                            last_window[app['process_name']] = current_title

if __name__ == "__main__":
    main()