import socket
import os

def handle_upload(conn, filename):
    filesize = int(conn.recv(1024).decode().strip()) 
    received = 0
    with open(f"uploads/{filename}", "wb") as f:  
         while received < filesize:
            chunk = conn.recv(4096)
            if not chunk:
                break
            f.write(chunk)
            received += len(chunk)

    conn.sendall(b"Upload successful")

def handle_download(conn, filename): 
    path = "uploads/"+filename
    if not os.path.exists(path):
        conn.sendall(f"404, 0".encode())
        return
    else: 
        filesize = os.path.getsize(path)
        conn.sendall(f"200, {filesize}".encode())
    with open(path, "rb") as f:  
        data = f.read(4096)
        if not data:
            return
        while data:
            conn.sendall(data)
            data = f.read(4096)

    print(f"file {filename} sent")

HOST = "127.0.0.1"
PORT = 65432

server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_sock.bind((HOST, PORT))
server_sock.listen()

while True:
    conn, addr = server_sock.accept()
    while True:
        data = conn.recv(1024).decode().strip()
        if not data:
            break
        if data == "/list":
            files = os.listdir("uploads")
            response = "\n".join(files)
            conn.sendall(response.encode())
        elif data.startswith("/upload"):
            filename = data.split()[1]
            handle_upload(conn, filename)
        elif data.startswith("/download"):
            filename = data.split()[1]
            handle_download(conn, filename)

    conn.close()
    print(f"client disconnected: {addr}")