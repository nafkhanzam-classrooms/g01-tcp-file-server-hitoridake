import socket, os, threading

listener_active = threading.Event()
listener_active.set() 

def receive_message(s):
    while True:
        try:
            if listener_active.wait(): 
                continue
            data = s.recv(4096).decode()
            if not data:
                break
            print(f"\n{data}")
        except:
            break

def upload_file(s, filename):
    listener_active.clear()
    filesize = os.path.getsize(filename)
    s.sendall(str(filesize).encode())
    s.recv(1024)
    with open(filename, "rb") as f:
        data = f.read(4096)
        while data:
            s.sendall(data)
            data = f.read(4096)
    response = s.recv(1024).decode()
    print(response)
    listener_active.set()

def download_file(s, filename):
    listener_active.clear()
    response = s.recv(1024).decode().strip()
    status, filesize = response.split(",")
    if status.strip() == "404":
        print(f"-- download failed: {filename} doesnt exist --")
        return
    print(f"-- downloading {filename}... --")
    filesize = int(filesize)
    received = 0
    with open(filename, "wb") as f:
        while received < filesize:
            chunk = s.recv(4096)
            if not chunk:
                break
            f.write(chunk)
            received += len(chunk)
    print(f"== successfully downloaded {filename} ==")
    listener_active.set()

HOST = '127.0.0.1'
PORT = 65432

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    print("== connection established ==")
    threading.Thread(target=receive_message, args=(s,), daemon=True).start()
    
    while True:
        buffer = input("command: ")
        part = buffer.split()
        command = part[0]
        filename = part[1] if len(part) > 1 else None

        if command == "-h":
            print("/list -- show list of available files")
            print("/upload <filename> -- upload a file")
            print("/download <filename> -- download a file")
            print("/exit -- disconnect")
        elif command == "/upload":
            s.sendall(buffer.encode())
            if not os.path.exists(filename):
                print("-- file doesn't exist --")
                continue
            upload_file(s, filename)
        elif command == "/download":
            s.sendall(buffer.encode())
            download_file(s, filename)
        elif command == "/list":
            s.sendall(command.encode())
            response = s.recv(4096).decode()
            print(response)
        elif command == "/exit":
            break