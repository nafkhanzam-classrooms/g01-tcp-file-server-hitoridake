import socket
import os

def upload_file(s, filename):
    path = input("file path: ")
    if not os.path.exists(path):
        print("upload failed: the specified file doesn't exist")
        return
    filesize = os.path.getsize(path)
    s.sendall(str(filesize).encode())
    with open(path, "rb") as f:  
        data = f.read(4096)
        if not data:
            return
        while data:
            s.send(data)
            data = f.read(4096)
    
    response = s.recv(1024).decode()
    print(response)

HOST = '127.0.0.1'
PORT = 65432

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    while True:
        print("type a command or -h for list of commands")
        buffer = input()
        part = buffer.split()
        command = part[0]
        filename = part[1] if len(part) > 1 else None

        if command == "-h":
            print("/list -- show list of available files\n")
            print("/upload <file_name> -- upload a file to the server\n")
            print("/download <file_name> -- download a file from the server\n")

        elif command == "/upload": 
            s.send((buffer).encode())
            upload_file(s, filename)
        elif command == "/download":
            #do something
        elif command == "/list"
            #do something
        else: 
            print("invalid command\n")
