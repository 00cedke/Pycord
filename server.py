import tkinter as tk
from flask import Flask, request, Response
from flask_socketio import SocketIO, emit
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
import threading
import xml.etree.ElementTree as ET

client = MongoClient('mongodb://127.0.0.1:27017/')
db = client['pycord']
users_collection = db['users']
messages_collection = db['messages']

app = Flask(__name__)
app.secret_key = ''
socketio = SocketIO(app)

def dict_to_xml(tag, d):
    """Converts a dictionary to an XML string"""
    elem = ET.Element(tag)
    for key, value in d.items():
        child = ET.SubElement(elem, key)
        child.text = str(value)
    return ET.tostring(elem, encoding='unicode')

def parse_xml(data):
    """Parses the XML request body and returns a dictionary"""
    root = ET.fromstring(data)
    parsed_data = {}
    for child in root:
        parsed_data[child.tag] = child.text
    return parsed_data

@app.route('/register', methods=['POST'])
def register():
    data = request.data.decode('utf-8')
    parsed_data = parse_xml(data)
    
    username = parsed_data.get('username')
    password = parsed_data.get('password')
    
    if users_collection.find_one({'username': username}):
        return Response(dict_to_xml('response', {'message': 'Username already taken'}), status=400, mimetype='application/xml')
    
    hashed_password = generate_password_hash(password)
    users_collection.insert_one({'username': username, 'password': hashed_password})
    
    return Response(dict_to_xml('response', {'message': 'User created successfully'}), status=201, mimetype='application/xml')

@app.route('/login', methods=['POST'])
def login():
    data = request.data.decode('utf-8')
    parsed_data = parse_xml(data)
    
    username = parsed_data.get('username')
    password = parsed_data.get('password')
    
    user = users_collection.find_one({'username': username})
    
    if not user or not check_password_hash(user['password'], password):
        return Response(dict_to_xml('response', {'message': 'Incorrect username or password'}), status=401, mimetype='application/xml')
    
    return Response(dict_to_xml('response', {'message': 'Connection successful'}), status=200, mimetype='application/xml')

@socketio.on('send_message')
def handle_message(data):
    username = data.get('username')
    message = data.get('message')
    messages_collection.insert_one({'username': username, 'message': message})
    emit('receive_message', {'username': username, 'message': message}, broadcast=True)

@app.route('/messages', methods=['GET'])
def get_messages():
    messages = list(messages_collection.find())
    
    messages_xml = '<messages>'
    for msg in messages:
        message_element = '<message>'
        message_element += f'<username>{msg["username"]}</username>'
        message_element += f'<message>{msg["message"]}</message>'
        message_element += '</message>'
        messages_xml += message_element
    messages_xml += '</messages>'
    
    return Response(messages_xml, mimetype='application/xml')

def run_server():
    socketio.run(app, host='0.0.0.0', port=5000, use_reloader=False)

if __name__ == '__main__':
    server_thread = threading.Thread(target=run_server)
    server_thread.start()
