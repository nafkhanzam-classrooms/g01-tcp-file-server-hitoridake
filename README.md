[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/mRmkZGKe)
# Network Programming - Assignment G01

## Anggota Kelompok
| Nama           | NRP        | Kelas     |
| ---            | ---        | ----------|
| Riyan Fadli Amazzadin               |     5025241068       |    D       |

## Link Youtube (Unlisted)
Link ditaruh di bawah ini
```

```

## Penjelasan Program
### Helper Function
Pada keempat file server, saya menggunakan fungsi helper yang sama yaitu `handle_upload()`, `handle_download()` dan `get_filename`(). Berikut adalah penjelasan ketiga function tersebut

1. `get_filename(path)`
   <br>
   
   ```python
    def get_filename(path):
        filename = os.path.basename(path)          
        name, ext = os.path.splitext(filename)     
        counter = 1
        result = filename
        while os.path.exists("uploads/" + result):
            result = f"{name}{counter}{ext}"       
            counter += 1
    
    return result
   ```
    Fungsi ini digunakan untuk mendapatkan nama dari file yang dikirim oleh client. Ini diperlukan karena saat client melakukan `/upload`, yang dimasukkan sebagai parameter pada pemanggilan command tersebut adalah directory full dari file yang ingin diupload.
     Pada implementasinya, saya menggunakan fungsi bawaan python yaitu `os.path.basename()`. Kemudian, saya juga memastikan apakah ada file dengan nama yang sama pada folder `uploads`. Jika ada, maka program akan menambahkan angka yang masih tersedia (`test1.txt, test2.txt, dst`) agar file yang sudah ada pada server tidak terhapus.
   <br>
   
2. `handle_upload(conn, path)`
   <br>

   ```python
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
   ```
   Fungsi ini digunakan untuk melayani perintah `/upload` dari client. Terdapat dua parameter yang digunakan yaitu `conn` yang merupakan client-server socket dan `path` yang merupakan full path dari file yang ingin diupload oleh client.
   Sebelum menerima file, server akan melakukan proses handshaking dengan client. Server akan menunggu hingga client mengirimkan ukuran dari file yang ingin dikirim, kemudian mengirimkan pesan `ready` untuk memberi tahu client bahwa proses upload file dapat dimulai. Server kemudian akan menerima byte data dari file yang dikirim client dan menuliskannya pada folder `uploads` dengan fungsi `open`. Setelah proses upload selesai, server memberi pesan upload successful kepada client. 

3. `handle_download(conn, filename)`
   <br>

   ```python
   def handle_download(conn, filename): 
       path = "uploads/"+filename
       if not os.path.exists(path):
           conn.sendall(f"404, 0".encode())
           return
       else: 
           filesize = os.path.getsize(path)
           conn.sendall(f"200, {filesize}".encode())
           conn.recv(1024)
       with open(path, "rb") as f:  
           data = f.read(4096)
           if not data:
               return
           while data:
               conn.sendall(data)
               data = f.read(4096)

    print(f"file {filename} sent")
   ```
   Fungsi ini digunakan untuk melayani perintah `/download` dari client. Sebelum mengirimkan file, server akan memastikan apakah file yang diminta oleh client memang ada tersedia pada server. Server akan mengirimkan pesan 200 beserta ukuran file jika ada, dan pesan 404 dan 0 jika file yang diminta tidak valid. Setelah itu, server membaca byte file dengan fungsi `open` dan mengirimkannya pada client.
   
### server-sync.py
```python
import socket, os

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
```

Proses utama server dijalankan pada nester while loop. While loop yang paling luar akan membuat socket baru dengan client, sedangkan loop yang kedua akan melayani permintaan client dengan memanggil fungsi yang sesuai. Kemudian ketika client menutup koneksi, server akan menutup socket dan menuliskan log ip dan port dari client yang terputus. 

Karena server bekerja secara synchronus, maka dalam 1 waktu server hanya bisa melayani 1 client. Client lain dalam antrian akan dilayani ketika client sebelumnya memutuskan koneksi dengan server. 

### server-select.py

```python 
import socket, os, select

def broadcast(message, input_sockets):
    for conn in input_sockets[:]:
        if conn != server_sock:
            try:
                conn.sendall(message.encode())
            except:
                input_sockets.remove(conn)

HOST = "127.0.0.1"
PORT = 65432

server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_sock.bind((HOST, PORT))
server_sock.listen(5)
input_sockets = [server_sock]

while True:
    read_ready, _, _ = select.select(input_sockets, [], [])
    for sock in read_ready:
        if sock == server_sock:
            conn, addr = server_sock.accept()
            input_sockets.append(conn)
            broadcast(f"new client connected: {addr[0]}:{addr[1]}\n", input_sockets)
        else:
            data = sock.recv(1024).decode().strip()
            if not data:
                print(f"client disconnected: {addr[0]}:{addr[1]}")
                input_sockets.remove(sock)
                sock.close()
            else:
                if data == "/list":
                    files = os.listdir("uploads")
                    sock.sendall("\n".join(files).encode())
                elif data.startswith("/upload"):
                    filename = data.split()[1]
                    handle_upload(sock, filename)
                elif data.startswith("/download"):
                    filename = data.split()[1]
                    handle_download(sock, filename)
                

```
Berbeda dengan `server-sync`, `server-select` memanfaatkan `select` untuk melakukan monitoring terhadap semua client yang terhubung dan melayani client yang telah mengirimkan pesan. Untuk melakukan ini, program menggunakan `read_ready` yang diperoleh dari fungsi `select.select` dengan list semua socket sebagai parameter. Jika socket client terdapat pada read_ready, hal ini mengindikasikan bahwa client telah mengirimkan pesan yang dapat dibaca oleh server. Karena itu server akan dengan segera menghandle permintaan dari client tersebut. 

Selain itu, pendekatan select memungkinkan server untuk berkomunikasi dengan seluruh client secara langsung. Maka di sini saya menambahkan function `broadcast` untuk mengirim pesan kepada semua client dengan memanfaatkan list `input_sockets`

### server-poll.py
```python
import socket, os, select
def broadcast(message, conn_map):
    for fd in list(conn_map.keys()):
        try:
            conn_map[fd].sendall(message.encode())
        except:
            del conn_map[fd]

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
            broadcast(f"new client connected: {addr[0]}:{addr[1]}", fd_map)
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
                
```
Polling bekerja dengan prinsip yang sama dengan select, yakni memonitor client mana yang telah mengirimkan pesan dan membutuhkan respon dari server. Perbedaannya terletak pada bagaimana poll melakukan monitoring tersebut. Alih-alih menerima socket object secara langsung, poll menggunakan file descriptor untuk membedakan antar socket sehingga diperlukan `fd_map` untuk melakukan mapping antara fd dengan socket object. Hal ini juga menjadikan implementasi fungsi broadcast memerlukan sedikit perubahan yaitu dengan melakukan iterasi pada fd_map.  Selain itu, poll menggunakan sistem flag seperti POLLIN untuk menentukan jenis event yang ingin dimonitor, sedangkan select menggunakan tiga list terpisah untuk read, write, dan error.

### server-thread.py
```python
import socket, os, threading

clients = []
lock = threading.Lock()

def broadcast(message):
    with lock:
        for client in clients:
            try:
                client.sendall(message.encode())
            except:
                clients.remove(client)

def handle_client(conn, addr):
    while True:
        data = conn.recv(1024).decode().strip()
        if not data:
            print(f"client disconnected: {addr[0]}:{addr[1]}")
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

    broadcast(f"goodbye {addr[0]}:{addr[1]}, we'll miss you!")
    with lock:
        clients.remove(conn)
    conn.close()


HOST = "127.0.0.1"
PORT = 65432

server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_sock.bind((HOST, PORT))
server_sock.listen(5)

while True:
    conn, addr = server_sock.accept()
    with lock:
        clients.append(conn)
    print(f"connected to: {addr[0]}:{addr[1]}")
    broadcast(f"new connected client! everyone say hi to {addr[0]}:{addr[1]}")
    threading.Thread(target=handle_client, args=(conn,addr)).start()

```
Berbeda dengan `server-sync`, `server-thread` memanfaatkan modul `threading` untuk melayani beberapa client secara bersamaan. Setiap kali ada client baru yang terhubung, server akan membuat thread baru yang menjalankan fungsi `handle_client` untuk melayani client tersebut. Dengan begitu, server dapat melayani banyak client secara paralel tanpa harus menunggu client sebelumnya memutuskan koneksi.

Untuk mengelola daftar client yang terhubung, program menggunakan list `clients` yang diakses bersama oleh semua thread. Karena list ini diakses secara bersamaan oleh banyak thread, digunakan `threading.Lock()`untuk memastikan hanya satu thread yang dapat memodifikasi list tersebut pada satu waktu, sehingga menghindari race condition.
Selain itu, fungsi broadcast digunakan untuk mengirim pesan kepada semua client yang terhubung. Fungsi ini juga menggunakan lock yang sama untuk memastikan keamanan saat mengiterasi list clients

### client.py
```python
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
    s.sendall(b"ready")
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
```
1. `receive_message()` <br>
   Digunakan untuk menerima pesan yang tidak berkaitan dengan command `/upload`, `/download`, maupun `/list`. Fungsi ini dijalankan menggunakan thread dan memanfaatkan Event berupa `listener_active()` untuk memastikan tidak terjadi race condition. Saat client melakukan proses upload maupun download, `listener_active()` akan dinonaktifkan sehingga fungsi receive_message() diblock sementara. <br>
   
2. `download`, `upload`, dan `list` <br>
   Fungsi `download_file()` dan `upload_file()` digunakan untuk menangani proses upload dan download, dengan prinsip kerja yang sama dengan `handle_download()` dan `handle_upload()` pada file server. Ketika client mengirimkan perintah `/upload <file>`, client akan mengirimkan pesan tersebut kepada server. Server kemudian akan bersiap menerima ukuran file yang akan dikirim. `upload_file()` pada client mengirim ukuran file, menunggu respon dari server, kemudian membuka file dan mengirimkan byte file ke server.
   
   Sedangkan pada proses download, setelah client mengirimkan `/download <file>` pada server, client akan menunggu respon apakah file yang diminta valid atau tidak. Setelah itu client akan mulai menerima byte file pada server.
   
   Sementar itu, saat client mengirimkan `/list`, client akan menunggu respon dari server dan menampilkannya. 

     
## Screenshot Hasil

### server-sync.py
<br>
<img width="1285" height="569" alt="image" src="https://github.com/user-attachments/assets/da8de58a-091f-49c3-b7d9-2410e896fe04" />
<br> <br>

Karena server bersifat synchronus, dapat dilihat bahwa client kedua (sebelah kanan) tidak mendapatkan response dari perintah `/list` karena server masih melayani client pertama. 
<br> <br>
<img width="1293" height="567" alt="image" src="https://github.com/user-attachments/assets/3a03b302-0472-4007-8abe-dc7a74c77d99" />
<br> <br>
Setelah client pertama memutuskan koneksi, client kedua mendapat respon dari server

### server-select.py
<br> 
<img width="1287" height="470" alt="image" src="https://github.com/user-attachments/assets/1e0170ea-5ff0-4443-9fd4-06c2adfc5a01" />
<br> <br>
Berbeda dengan pendekatan synchronus, pada server-select dapat dilihat bahwa client kedua mendapatkan repon dari server meskipun client pertama masih terhubung. Selain itu, server juga dapat mengirimkan pesan broadcast kepada seluruh client yang terhubung sekaligus. 

### server-poll.py
<br>
<img width="1364" height="515" alt="image" src="https://github.com/user-attachments/assets/e7b526aa-53f7-4463-ab8e-444d93f5fafc" />
<br> <br>
Sama seperti server-select, kedua client dapat ditangani secara langsung tanpa menunggu salah satu memutuskan koneksi.

### server-thread.py
<br>
<img width="1584" height="390" alt="image" src="https://github.com/user-attachments/assets/4937a7c0-9e6e-4ca7-90a1-0c9b7588dfe2" />

