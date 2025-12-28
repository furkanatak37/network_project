import socket
import threading
import time
import os
import sys

INDEX_IP = "127.0.0.1"
INDEX_PORT = 5000
MONITOR_IP = "127.0.0.1"
MONITOR_UDP_PORT = 6000

BUFFER_SIZE = 4096
HEARTBEAT_INTERVAL = 3

active_clients = 0
lock = threading.Lock()


def handle_client(conn, addr, files_dir):
    global active_clients

    print(f"->Client connected from {addr}")

    with lock:
        active_clients += 1

    try:
        request = conn.recv(BUFFER_SIZE).decode().strip()
        _, file_name = request.split()

        file_path = os.path.join(files_dir, file_name)

        if not os.path.exists(file_path):
            print(f" File not found: {file_name}")
            conn.sendall(b"ERROR FILE_NOT_FOUND\n")
            return

        file_size = os.path.getsize(file_path)
        print(f"-> Sending file: {file_name} ({file_size} bytes)")
        conn.sendall(f"OK {file_size}\n".encode())

        with open(file_path, "rb") as f:
            while True:
                data = f.read(BUFFER_SIZE)
                if not data:
                    break
                conn.sendall(data)
                time.sleep(2)


    finally:
        conn.close()
        with lock:
            active_clients -= 1
        print(f"🔌 Client disconnected: {addr}")



def tcp_server(tcp_port, files_dir):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("", tcp_port))
    server.listen(5)

    print(f"Content Server TCP listening: {tcp_port}")

    while True:
        conn, addr = server.accept()
        threading.Thread(
            target=handle_client,
            args=(conn, addr, files_dir),
            daemon=True
        ).start()


def heartbeat(server_id, tcp_port, udp_port, files_dir):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    while True:
        with lock:
            load = active_clients

        num_files = len(os.listdir(files_dir))
        msg = f"HEARTBEAT {server_id} 127.0.0.1 {tcp_port} {load} {num_files}"
        sock.sendto(msg.encode(), (MONITOR_IP, MONITOR_UDP_PORT))

        time.sleep(HEARTBEAT_INTERVAL)


def register_with_index(server_id, tcp_port, udp_port, files_dir):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((INDEX_IP, INDEX_PORT))

    sock.sendall(f"REGISTER {server_id} {tcp_port} {udp_port}\n".encode())
    print(sock.recv(BUFFER_SIZE).decode().strip())

    for file_name in os.listdir(files_dir):
        file_path = os.path.join(files_dir, file_name)
        if os.path.isfile(file_path):
            size = os.path.getsize(file_path)
            sock.sendall(f"ADD_FILE {server_id} {file_name} {size}\n".encode())

    sock.sendall(b"DONE_FILES\n")
    print(sock.recv(BUFFER_SIZE).decode().strip())

    sock.close()


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python content_server.py <server_id> <tcp_port> <files_dir>")
        sys.exit(1)

    server_id = sys.argv[1]
    tcp_port = int(sys.argv[2])
    files_dir = sys.argv[3]
    udp_port = tcp_port + 1

    register_with_index(server_id, tcp_port, udp_port, files_dir)

    threading.Thread(
        target=heartbeat,
        args=(server_id, tcp_port, udp_port, files_dir),
        daemon=True
    ).start()

    tcp_server(tcp_port, files_dir)
