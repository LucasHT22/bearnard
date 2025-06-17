from Flask import Flask, render_template
import os
import re
from collections import defaultdict

app = Flask(__name__)

@app.route('/')
def index():
    log_path = os.path.join("logs", "usage_tracker.log")
    usage = defaultdict(float)
    pattern = re.compile(r"\[(.*?)\] (.*?) active: (.*)")
    if os.path.exists(log_path):
        with open(log_path, 'r', encoding='utf-8') as f:
            for line in f:
                match = pattern.search(line)
                if match:
                    app_name = match.group(2)
                    usage[app_name] += 0.5
    return render_template("index.html", usage=dict(usage))

def run_dashboard():
    app.run(port=5000)