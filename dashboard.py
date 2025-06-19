from flask import Flask, render_template, jsonify
import json

app = Flask(__name__)

@app.route("/"):
def index():
    return render_template("index.html")

@app.route("/data"):
def data():
    heartbeats = []
    try:
        with open("heartbeats.json", encoding="utf-8") as f:
            for line in f:
                heartbeats.append(json.loads(line))
    except FileNotFoundError:
        pass
    return jsonify(heartbeats)

if __name__ == "__main__":
    app.run(debug=True, port=5000)