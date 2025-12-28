import socket
import threading

INDEX_PORT = 5000
MONITOR_IP = "127.0.0.1"
MONITOR_TCP_PORT = 6001
BUFFER_SIZE = 4096

servers = {}  # server_id -> info
files = {}    # file_name -> list of (server_id, size)
lock = threading.Lock()


def handle_connection(conn):
    try:
        while True:
            data = conn.recv(BUFFER_SIZE)
            if not data:
                break

            msg = data.decode().strip().split()
            cmd = msg[0]

            # -------- Content Server --------
            if cmd == "REGISTER":
                _, server_id, tcp_port, udp_port = msg
                with lock:
                    servers[server_id] = {
                        "ip": conn.getpeername()[0],
                        "tcp_port": int(tcp_port),
                        "status": "ALIVE"
                    }
                conn.sendall(b"OK REGISTERED\n")

            elif cmd == "ADD_FILE":
                _, server_id, file_name, size = msg
                with lock:
                    files.setdefault(file_name, []).append((server_id, int(size)))

            elif cmd == "DONE_FILES":
                conn.sendall(b"OK FILES_ADDED\n")

            # -------- Client --------
            elif cmd == "HELLO":
                conn.sendall(b"WELCOME MICRO-CDN\n")

            elif cmd == "GET":
                _, file_name = msg
                with lock:
                    if file_name not in files:
                        conn.sendall(b"ERROR FILE_NOT_FOUND\n")
                        continue

                    # canlı server seç
                    alive_servers = [
                        (sid, size) for sid, size in files[file_name]
                        if servers.get(sid, {}).get("status") == "ALIVE"
                    ]

                    if not alive_servers:
                        conn.sendall(b"ERROR FILE_NOT_FOUND\n")
                        continue

                    server_id, size = alive_servers[0]
                    s = servers[server_id]
                    response = f"SERVER {s['ip']} {s['tcp_port']} {server_id} {size}\n"
                    conn.sendall(response.encode())

            # -------- Monitor --------
            elif cmd == "SERVER_DOWN":
                _, server_id, _ = msg
                with lock:
                    if server_id in servers:
                        servers[server_id]["status"] = "DEAD"
                        print(f"Index: {server_id} DEAD")

            else:
                conn.sendall(b"ERROR UNKNOWN_COMMAND\n")

    finally:
        conn.close()


def connect_to_monitor():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((MONITOR_IP, MONITOR_TCP_PORT))
    print("📡 Index → Monitor connected")

    while True:
        data = sock.recv(BUFFER_SIZE)
        if not data:
            break

        msg = data.decode().strip().split()
        if msg[0] == "SERVER_DOWN":
            _, server_id, _ = msg
            with lock:
                if server_id in servers:
                    servers[server_id]["status"] = "DEAD"
                    print(f"Monitor notification: {server_id} DOWN")


def tcp_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("", INDEX_PORT))
    sock.listen(10)
    print(f"📚 Index Server listening: {INDEX_PORT}")

    while True:
        conn, _ = sock.accept()
        threading.Thread(
            target=handle_connection,
            args=(conn,),
            daemon=True
        ).start()


if __name__ == "__main__":
    threading.Thread(target=connect_to_monitor, daemon=True).start()
    tcp_server()
