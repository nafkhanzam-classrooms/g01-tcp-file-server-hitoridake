import socket
import os

def upload_file(s, filename):
    path = input("file path: ")
    if not os.path.exists(path):
        print("-- upload failed: the specified file doesn't exist --")
        return
    filesize = os.path.getsize(path)
    s.sendall(str(filesize).encode())
    with open(path, "rb") as f:  
        data = f.read(4096)
        if not data:
            return
        while data:
            s.sendall(data)
            data = f.read(4096)
    
    response = s.recv(1024).decode()
    print(response)

def download_file(s, filename):
    response = s.recv(1024).decode().strip()
    status, filesize = response.split(",")
    if status == "404":
        print(f"-- download failed: {filename} doesnt exist --")
    elif status == "200":
        print(f"-- downloading {filename}... --")
        filesize = int(filesize)
    received = 0
    with open(f"{filename}", "wb") as f:  
         while received < filesize:
            chunk = s.recv(4096)
            if not chunk:
                break
            f.write(chunk)
            received += len(chunk)

    print(f"== successfully downloaded {filename} ==")


HOST = '127.0.0.1'
PORT = 65432

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    print("== connection established ==")
    while True:
        buffer = input("command: ")
        part = buffer.split()
        command = part[0]
        filename = part[1] if len(part) > 1 else None

        if command == "-h":
            print("== command lists == ")
            print("/list -- show list of available files\n")
            print("/upload <file_name> -- upload a file to the server\n")
            print("/download <file_name> -- download a file from the server\n")
            print("/exit to stop the client")
            print(" ================ ")
        elif command == "/upload": 
            s.sendall((buffer).encode())
            upload_file(s, filename)
        elif command == "/download":
            s.sendall((buffer).encode())
            download_file(s, filename)
        elif command == "/list":
            s.sendall((command).encode())
            list = s.recv(4096).decode()
            print(list)
        elif command == "/exit":
            break
        else: 
            print("-- invalid command. type -h for list of available commands\n --")
