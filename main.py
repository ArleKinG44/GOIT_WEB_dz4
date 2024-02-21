from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn, UDPServer, BaseRequestHandler
from urllib.parse import parse_qs
import socket
import os
import json
from datetime import datetime
import threading

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    pass

class HTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = '/index.html'
        try:
            file_path = os.getcwd() + self.path
            if self.path.endswith('.html') or self.path.endswith('.css') or self.path.endswith('.png'):
                with open(file_path, 'rb') as file:
                    self.send_response(200)
                    if self.path.endswith('.html'):
                        self.send_header('Content-type', 'text/html')
                    elif self.path.endswith('.css'):
                        self.send_header('Content-type', 'text/css')
                    elif self.path.endswith('.png'):
                        self.send_header('Content-type', 'image/png')
                    self.end_headers()
                    self.wfile.write(file.read())
            else:
                self.send_error(404, 'File Not Found: %s' % self.path)
        except Exception as e:
            print(str(e))

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        parsed_data = parse_qs(post_data)
        self.send_response(200)
        self.end_headers()

        data = {'username': parsed_data['username'][0], 'message': parsed_data['message'][0]}
        socket_client.send_data(json.dumps(data).encode())

        self.wfile.write(bytes('<html><head><meta http-equiv="refresh" content="0;url=/message.html"></head><body></body></html>', 'utf-8'))

def start_http_server():
    server_address = ('', 3000)
    httpd = ThreadedHTTPServer(server_address, HTTPRequestHandler)
    print('HTTP Server running on port 3000...')
    httpd.serve_forever()

class UDPRequestHandler(BaseRequestHandler):
    def handle(self):
        data = self.request[0].strip()
        socket_server.handle_data(data)

class SocketServer:
    def __init__(self):
        self.server_address = ('', 5000)
        self.server = UDPServer(self.server_address, UDPRequestHandler)
        print('Socket Server running on port 5000...')

    def handle_data(self, data):
        try:
            data_dict = json.loads(data.decode())
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
            data_dict = {timestamp: data_dict}
            with open('storage/data.json', 'a') as file:
                json.dump(data_dict, file, indent=2)
                file.write('\n')
        except Exception as e:
            print('Error handling data:', str(e))

    def run(self):
        self.server.serve_forever()

class SocketClient:
    def __init__(self, server_address, server_port):
        self.server_address = server_address
        self.server_port = server_port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send_data(self, data):
        self.client_socket.sendto(data, (self.server_address, self.server_port))

socket_client = SocketClient('localhost', 5000)

if __name__ == "__main__":
    socket_server = SocketServer()
    threading.Thread(target=start_http_server).start()
    socket_thread = threading.Thread(target=socket_server.run)
    socket_thread.daemon = True
    socket_thread.start()
