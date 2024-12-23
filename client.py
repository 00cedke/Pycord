import tkinter as tk
from tkinter import messagebox
import socketio
import threading
import requests

class ChatApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Pycord")
        self.geometry("600x500")
        
        self.sio = socketio.Client()
        self.sio.connect('http://localhost:5000')

        self.username_entry = tk.Entry(self)
        self.username_entry.pack(pady=10)
        
        self.password_entry = tk.Entry(self, show="*")
        self.password_entry.pack(pady=10)
        
        self.login_button = tk.Button(self, text="Login", command=self.login)
        self.login_button.pack(pady=5)

        self.register_button = tk.Button(self, text="Create", command=self.register)
        self.register_button.pack(pady=5)

        self.chat_frame = tk.Frame(self)
        self.chat_text = tk.Text(self.chat_frame, height=20, width=50, state=tk.DISABLED)
        self.chat_text.pack()

        self.message_entry = tk.Entry(self.chat_frame)
        self.message_entry.pack(pady=5)

        self.send_button = tk.Button(self.chat_frame, text="Send", command=self.send_message)
        self.send_button.pack(pady=5)
        
        self.chat_frame.pack_forget()

        self.sio.on('receive_message', self.receive_message)

    def send_message(self):
        message = self.message_entry.get()
        if message:
            self.sio.emit('send_message', {'username': self.username, 'message': message})
            self.message_entry.delete(0, tk.END)

    def receive_message(self, data):
        message = f"{data['username']}: {data['message']}\n"
        self.chat_text.config(state=tk.NORMAL)
        self.chat_text.insert(tk.END, message)
        self.chat_text.config(state=tk.DISABLED)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror("Error", "Please fill in all fields")
            return
        
        requests.post("http://localhost:5000/login", json={"username": username, "password": password})

        self.username = username
        self.show_chat()

    def register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror("Error", "Please fill in all fields")
            return
        
        requests.post("http://localhost:5000/register", json={"username": username, "password": password})
        
        self.username = username
        self.show_chat()

    def show_chat(self):
        self.username_entry.pack_forget()
        self.password_entry.pack_forget()
        self.login_button.pack_forget()
        self.register_button.pack_forget()
        
        self.chat_frame.pack()

if __name__ == '__main__':
    app = ChatApp()
    app.mainloop()
