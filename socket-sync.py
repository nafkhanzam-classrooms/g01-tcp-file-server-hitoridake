import socket

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

def handle_download(conn, filename): ...
def get_all_files(): ...

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
            # get_all_files()
            print("optained list")
        elif data.startswith("/upload"):
            filename = data.split()[1]
            handle_upload(conn, filename)
        elif data.startswith("/download"):
            filename = data.split()[1]
            # handle_download(conn, filename)
            print(f"{filename}")

    conn.close()
    print(f"client disconnected: {addr}")