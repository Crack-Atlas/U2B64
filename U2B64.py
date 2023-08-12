import http.server
import socketserver
import base64
import os
import urllib.parse
import cgi
import webbrowser 

PORT =1998

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
<style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 0;
                }
                h1 {
                    text-align: center;
                    margin: 20px 0;
                }
                .filec {
                    max-width: 800px;
                    margin-top: 20px;
                    padding: 20px;
                    background-color: grey;
                    box-shadow: 0 0 10px rgba(0,0,0,0.2);
                }
                form input[type="file"] {
                    margin: 10px 0;
                }
                .fnx{
                text-color: black; 
                text-align: center;
                margin: 20px 0;
                } 
                </style> 
 <meta charset="UTF-8">
 <meta name="viewport" content="width=device-width, initial-scale=1.0">
 <meta http-equiv="X-UA-Compatible" content="ie=edge">
 <title>U2B64</title>
</head>
<body bgcolor='black'>
<center> 
<div class='filec'> 
                <form action="/upload" method="post" enctype="multipart/form-data">
                    <input type="file" name="file" class='fnx'><br>
                    <input type="submit" value="Upload">
                </form>
                </div> 
                <br>
                <button><a href="/list">View Encrypted Files</a></button>
                </center> 
            </body>
            </html> 
            ''')
        elif parsed_path.path == '/list':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            encrypted_files = []
            for filename in os.listdir('.'):
                if filename.endswith('.encrypted'):
                    encrypted_files.append(filename)
            self.wfile.write(b'''
            <!DOCTYPE html>
<html lang="en">
<head>
<style>                body {
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 0;
                    background-color: #f0f0f0;
                }
                h1 {
                    text-align: center;
                    margin: 20px 0;
                }
                .container {
                    max-width: 800px;
                    margin-top: 20px;
                    padding: 20px;
                    background-color: grey;
                    box-shadow: 0 0 10px rgba(0,0,0,0.2);
                }
                form input[type="file"] {
                    margin: 10px 0;
                }

                .file-list li {
                    margin-bottom: 10px;
                }
                .file-list a {
                    text-decoration: none;
                    color: #000;
                }
                </style> 
 <meta charset="UTF-8">
 <meta name="viewport" content="width=device-width, initial-scale=1.0">
 <meta http-equiv="X-UA-Compatible" content="ie=edge">
 <title>U264 E-list</title>
</head>
<body>
<center>
                <h2>Encrypted Files:</h2>
                <div class='container'> 
            ''')
            for filename in encrypted_files:
                self.wfile.write(f'<p><a href="/decrypt/{filename}">{filename}</a></p>'.encode('utf-8'))
            self.wfile.write(b'''
            </div> 
            </center> 
            </body>
            </html>
            ''')
        elif parsed_path.path.startswith('/decrypt/'):
            filename = parsed_path.path[9:]
            with open(filename, 'rb') as f:
                encrypted_content = f.read()
            decrypted_content = base64.b64decode(encrypted_content)
            self.send_response(200)
            self.send_header('Content-type', 'application/octet-stream')
            self.send_header('Content-Disposition', f'attachment; filename="{filename[:-10]}"')
            self.end_headers()
            self.wfile.write(decrypted_content)
        else:
            self.send_error(404)

    def do_POST(self):
        parsed_path = urllib.parse.urlparse(self.path)
        if parsed_path.path == '/upload':
            content_type, _ = cgi.parse_header(self.headers['content-type'])
            if content_type == 'multipart/form-data':
                form_data = cgi.FieldStorage(
                    fp=self.rfile,
                    headers=self.headers,
                    environ={'REQUEST_METHOD': 'POST'}
                )
                uploaded_file = form_data['file']
                if uploaded_file.filename != '':
                    file_content = uploaded_file.file.read()
                    encrypted_content = base64.b64encode(file_content)
                    with open(uploaded_file.filename + '.encrypted', 'wb') as f:
                        f.write(encrypted_content)
            self.send_response(302)
            self.send_header('Location', '/')
            self.end_headers()
        else:
            self.send_error(404)

with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
    print(f"Serving at port {PORT}")
    webbrowser.open_new_tab(f'http://localhost:{PORT}')
    httpd.serve_forever()