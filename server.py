import tkinter as tk
from flask import Flask, jsonify, request
from flask_socketio import SocketIO, emit
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
import threading

client = MongoClient('mongodb://localhost:27017/')
db = client['pycord']
users_collection = db['users']
messages_collection = db['messages']

app = Flask(__name__)
app.secret_key = 'secret_key'
socketio = SocketIO(app)

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if users_collection.find_one({'username': username}):
        return jsonify({'message': 'Username already taken'}), 400
    
    hashed_password = generate_password_hash(password)
    users_collection.insert_one({'username': username, 'password': hashed_password})
    
    return jsonify({'message': 'User created successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    user = users_collection.find_one({'username': username})
    
    if not user or not check_password_hash(user['password'], password):
        return jsonify({'message': 'Incorrect username or password'}), 401
    
    return jsonify({'message': 'Connection successful'}), 200

@socketio.on('send_message')
def handle_message(data):
    username = data.get('username')
    message = data.get('message')
    messages_collection.insert_one({'username': username, 'message': message})
    emit('receive_message', {'username': username, 'message': message}, broadcast=True)

@app.route('/messages', methods=['GET'])
def get_messages():
    messages = list(messages_collection.find())
    return jsonify(messages), 200

def run_server():
    socketio.run(app, host='0.0.0.0', port=5000, use_reloader=False)

if __name__ == '__main__':
    server_thread = threading.Thread(target=run_server)
    server_thread.start()
