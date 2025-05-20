from flask import Flask
import subprocess

# This is the important part: defining 'app'
app = Flask(__name__)

@app.route("/")
def home():
    return "Nology Product Sync Web Service is running."

@app.route("/sync")
def trigger_sync():
    result = subprocess.run(["python", "cron/main.py"], capture_output=True, text=True)
    return f"<pre>{result.stdout or result.stderr}</pre>"

if __name__ == "__main__":
    app.run()