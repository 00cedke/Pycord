import logging
from flask import Flask, request, Response
import requests

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

TARGET_SERVER_URL = 'http://127.0.0.1:5000'

@app.route('/proxy', methods=['GET'])
def proxy_get():
    query_string = request.query_string.decode('utf-8')
    logging.info(f"Received GET request with query: {query_string}")

    target_url = f"{TARGET_SERVER_URL}/messages?{query_string}"
    response = requests.get(target_url, headers=request.headers)

    if 'application/xml' in response.headers.get('Content-Type', '') or 'text/xml' in response.headers.get('Content-Type', ''):
        logging.info(f"XML response received from target server (status code {response.status_code}):")
        logging.info(response.text)
    else:
        logging.error(f"Expected XML but got {response.headers.get('Content-Type')}")

    return Response(response.text, content_type=response.headers['Content-Type'], status=response.status_code)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
