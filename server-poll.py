import socket, os, select

def get_filename(path):
    filename = os.path.basename(path)
    name, ext = os.path.splitext(filename)
    counter = 1
    result = filename
    while os.path.exists("uploads/" + result):
        result = f"{name}{counter}{ext}"
        counter += 1
    return result

def broadcast(message, conn_map):
    for fd in list(conn_map.keys()):
        try:
            conn_map[fd].sendall(message.encode())
        except:
            del conn_map[fd]

def handle_upload(conn, path):
    filename = get_filename(path)
    filesize = int(conn.recv(1024).decode().strip())
    conn.sendall(b"ready")
    received = 0
    with open(f"uploads/{filename}", "wb") as f:
        while received < filesize:
            chunk = conn.recv(4096)
            if not chunk:
                break
            f.write(chunk)
            received += len(chunk)
    conn.sendall(b"== upload successful ==")
    print(f"uploaded {filename}")

def handle_download(conn, filename):
    path = "uploads/" + filename
    if not os.path.exists(path):
        conn.sendall(f"404, 0".encode())
        return
    filesize = os.path.getsize(path)
    conn.sendall(f"200, {filesize}".encode())
    with open(path, "rb") as f:
        data = f.read(4096)
        while data:
            conn.sendall(data)
            data = f.read(4096)
    print(f"file {filename} sent")

HOST = "127.0.0.1"
PORT = 65432
server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_sock.bind((HOST, PORT))
server_sock.listen(5)

poller = select.poll()                                    
poller.register(server_sock, select.POLLIN)               

fd_map = {}                                               
fd_map[server_sock.fileno()] = server_sock
addr_map = {}                                             

while True:
    events = poller.poll()                                
    for fd, event in events:                             
        if fd == server_sock.fileno():                  
            conn, addr = server_sock.accept()
            poller.register(conn, select.POLLIN)         
            fd_map[conn.fileno()] = conn
            addr_map[conn.fileno()] = addr
            broadcast(f"new client connected: {addr[0]}:{addr[1]}\n\n", fd_map)
        elif event & select.POLLIN:                       
            conn = fd_map[fd]
            addr = addr_map[fd]
            data = conn.recv(1024).decode().strip()
            if not data:                                  
                broadcast(f"client disconnected: {addr[0]}:{addr[1]}", fd_map)
                poller.unregister(conn)
                del fd_map[fd]
                del addr_map[fd]
                conn.close()
            else:
                if data == "/list":
                    files = os.listdir("uploads")
                    conn.sendall("\n".join(files).encode())
                elif data.startswith("/upload"):
                    filename = data.split()[1]
                    handle_upload(conn, filename)
                elif data.startswith("/download"):
                    filename = data.split()[1]
                    handle_download(conn, filename)
                