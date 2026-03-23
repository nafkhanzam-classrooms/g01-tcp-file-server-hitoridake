def upload_file(s, filename):
    filesize = os.path.getsize(filename)
    s.sendall(str(filesize).encode())
    with open(filename, "rb") as f:  
        data = f.read(4096)
        if not data:
            return
        while data:
            s.sendall(data)
            data = f.read(4096)
    
    response = s.recv(1024).decode()
    print(response)
