import http.server
import socketserver
import base64
import os
import urllib.parse
from email.parser import BytesParser
from email.policy import default
import webbrowser

PORT = 1998

class MyHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        if parsed_path.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'''
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>File Uploader</title>
                <style>
                    body {
                        font-family: Arial, sans-serif;
                        background-color: #f4f4f4;
                        margin: 0;
                        padding: 0;
                    }
                    .container {
                        max-width: 600px;
                        margin: 50px auto;
                        padding: 20px;
                        background-color: #fff;
                        box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                        border-radius: 8px;
                        text-align: center;
                    }
                    h1 {
                        margin-bottom: 20px;
                        color: #333;
                    }
                    form {
                        margin-bottom: 20px;
                    }
                    input[type="file"] {
                        padding: 10px;
                        border: 1px solid #ddd;
                        border-radius: 4px;
                        margin-bottom: 20px;
                    }
                    input[type="submit"] {
                        padding: 10px 20px;
                        background-color: #007bff;
                        color: #fff;
                        border: none;
                        border-radius: 4px;
                        cursor: pointer;
                    }
                    input[type="submit"]:hover {
                        background-color: #0056b3;
                    }
                    .file-list {
                        text-align: left;
                    }
                    .file-list a {
                        text-decoration: none;
                        color: #007bff;
                    }
                    .file-list a:hover {
                        text-decoration: underline;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Upload a File</h1>
                    <form action="/upload" method="post" enctype="multipart/form-data">
                        <input type="file" name="file" required><br>
                        <input type="submit" value="Upload">
                    </form>
                    <a href="/list">View Encrypted Files</a>
                </div>
            </body>
            </html>
            ''')
        elif parsed_path.path == '/list':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            encrypted_files = [f for f in os.listdir('.') if f.endswith('.encrypted')]
            self.wfile.write(b'''
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Encrypted Files</title>
                <style>
                    body {
                        font-family: Arial, sans-serif;
                        background-color: #f4f4f4;
                        margin: 0;
                        padding: 0;
                    }
                    .container {
                        max-width: 600px;
                        margin: 50px auto;
                        padding: 20px;
                        background-color: #fff;
                        box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                        border-radius: 8px;
                        text-align: center;
                    }
                    h1 {
                        margin-bottom: 20px;
                        color: #333;
                    }
                    .file-list {
                        text-align: left;
                    }
                    .file-list a {
                        text-decoration: none;
                        color: #007bff;
                    }
                    .file-list a:hover {
                        text-decoration: underline;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Encrypted Files</h1>
                    <div class="file-list">
            ''')
            for filename in encrypted_files:
                self.wfile.write(f'<p><a href="/decrypt/{filename}">{filename}</a></p>'.encode('utf-8'))
            self.wfile.write(b'''
                    </div>
                    <a href="/">Upload Another File</a>
                </div>
            </body>
            </html>
            ''')
        elif parsed_path.path.startswith('/decrypt/'):
            filename = parsed_path.path[9:]
            if os.path.isfile(filename):
                with open(filename, 'rb') as f:
                    encrypted_content = f.read()
                decrypted_content = base64.b64decode(encrypted_content)
                self.send_response(200)
                self.send_header('Content-type', 'application/octet-stream')
                self.send_header('Content-Disposition', f'attachment; filename="{filename[:-10]}"')
                self.end_headers()
                self.wfile.write(decrypted_content)
            else:
                self.send_error(404, "File not found")
        else:
            self.send_error(404, "Not found")

    def do_POST(self):
        parsed_path = urllib.parse.urlparse(self.path)
        if parsed_path.path == '/upload':
            content_length = int(self.headers['Content-Length'])
            boundary = self.headers['Content-Type'].split('=')[1].encode()
            body = self.rfile.read(content_length)
            parts = body.split(b'--' + boundary)
            for part in parts:
                if b'Content-Disposition: form-data;' in part:
                    headers, content = part.split(b'\r\n\r\n', 1)
                    headers = headers.decode().split('\r\n')
                    filename = None
                    for header in headers:
                        if header.startswith('Content-Disposition'):
                            filename = header.split('filename=')[1].strip('"')
                            break
                    if filename:
                        file_content = content.rsplit(b'\r\n--', 1)[0]
                        encrypted_content = base64.b64encode(file_content)
                        with open(filename + '.encrypted', 'wb') as f:
                            f.write(encrypted_content)
            self.send_response(302)
            self.send_header('Location', '/')
            self.end_headers()
        else:
            self.send_error(404, "Not found")

with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
    print(f"Serving at port {PORT}")
    webbrowser.open_new_tab(f'http://localhost:{PORT}')
    httpd.serve_forever()
