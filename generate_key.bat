@echo off
setlocal

where openssl >nul 2>nul
if %errorlevel% neq 0 (
    echo OpenSSL is not installed. Please install it to use this script.
    exit /b 1
)

openssl rand -out aes_key.bin 32

openssl enc -base64 -in aes_key.bin -out aes_key.txt

set /p AES_KEY=<aes_key.txt

rem
(
    echo # Flask application and SocketIO setup
    echo from flask import Flask
    echo from flask_socketio import SocketIO
    echo.
    echo app = Flask(__name__)
    echo app.secret_key = '%AES_KEY%'
    echo socketio = SocketIO(app)
) > server.py

echo The AES key has been generated and inserted into server.py

endlocal
pause
