import socket
import sys

INDEX_IP = "127.0.0.1"
INDEX_PORT = 5000
BUFFER_SIZE = 4096


def download_file(file_name):
    # 1️⃣ Index Server'a bağlan
    # Index Server'a bağlan
    index_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    index_sock.connect((INDEX_IP, INDEX_PORT))

    # SADECE GET gönder
    index_sock.sendall(f"GET {file_name}\n".encode())

    response = index_sock.recv(BUFFER_SIZE).decode().strip()
    print("DEBUG Index response:", response)
    index_sock.close()


    if response.startswith("ERROR"):
        print("❌ Index Server:", response)
        return

    # SERVER <ip> <port> <server_id> <file_size>
    parts = response.split()
    server_ip = parts[1]
    server_port = int(parts[2])
    file_size = int(parts[4])

    print(f"✅ Dosya bulundu → {server_ip}:{server_port} ({file_size} byte)")

    # 2️⃣ Content Server'a bağlan
    content_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    content_sock.connect((server_ip, server_port))

    content_sock.sendall(f"GET {file_name}\n".encode())

    header = content_sock.recv(BUFFER_SIZE).decode().strip()

    if header.startswith("ERROR"):
        print("❌ Content Server:", header)
        content_sock.close()
        return

    # OK <file_size>
    _, size_str = header.split()
    expected_size = int(size_str)

    received = 0
    data = b""

    while received < expected_size:
        chunk = content_sock.recv(BUFFER_SIZE)
        if not chunk:
            break
        data += chunk
        received += len(chunk)

    content_sock.close()

    # Dosyayı kaydet
    with open(file_name, "wb") as f:
        f.write(data)

    print(f"📁 Dosya indirildi: {file_name} ({received} byte)")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Kullanım: python client.py <dosya_adi>")
        sys.exit(1)

    download_file(sys.argv[1])
