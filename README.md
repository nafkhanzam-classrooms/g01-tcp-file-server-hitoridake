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

## Screenshot Hasil

### server-sync.py
<br>
<img width="1285" height="569" alt="image" src="https://github.com/user-attachments/assets/da8de58a-091f-49c3-b7d9-2410e896fe04" />
<br>

Karena server bersifat synchronus, dapat dilihat bahwa client kedua (sebelah kanan) tidak mendapatkan response dari perintah `/list` karena server masih melayani client pertama. 
<br>
<img width="1293" height="567" alt="image" src="https://github.com/user-attachments/assets/3a03b302-0472-4007-8abe-dc7a74c77d99" />
<br>
Setelah client pertama memutuskan koneksi, client kedua mendapat respon dari server


