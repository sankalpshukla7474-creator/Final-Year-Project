# Correct Code for iot_server.py
from flask import Flask
from datetime import datetime

app = Flask(__name__)
LOG_FILE = 'phone_presence.log'

@app.route('/heartbeat')
def receive_heartbeat():
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_message = f"Phone signal received at: {timestamp}\n"
    with open(LOG_FILE, 'a') as f:
        f.write(log_message)
    print(log_message.strip()) # .strip() removes the extra newline for cleaner terminal output
    return "OK"

if __name__ == '__main__':
    print("IoT Server is running. Listening for signals from the phone...")
    print("Make sure your laptop and phone are on the same Wi-Fi network.")
    app.run(host='0.0.0.0', port=5000)