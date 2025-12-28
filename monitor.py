import socket
import threading
import time

UDP_PORT = 6000
TCP_PORT = 6001
BUFFER_SIZE = 4096
TIMEOUT = 8  # saniye

# server_id -> info
servers = {}
lock = threading.Lock()

index_connections = []  # Index Server TCP bağlantıları


def udp_listener():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("", UDP_PORT))
    print(f"🩺 Monitor UDP dinliyor: {UDP_PORT}")

    while True:
        data, _ = sock.recvfrom(BUFFER_SIZE)
        msg = data.decode().strip().split()

        if msg[0] != "HEARTBEAT":
            continue

        _, server_id, ip, tcp_port, load, num_files = msg

        with lock:
            servers[server_id] = {
                "ip": ip,
                "tcp_port": tcp_port,
                "load": load,
                "num_files": num_files,
                "last_seen": time.time(),
                "status": "ALIVE"
            }


def timeout_checker():
    while True:
        time.sleep(1)
        now = time.time()

        with lock:
            for server_id, info in list(servers.items()):
                if info["status"] == "ALIVE" and now - info["last_seen"] > TIMEOUT:
                    info["status"] = "DEAD"
                    print(f"❌ SERVER DOWN: {server_id}")
                    notify_index(server_id)


def notify_index(server_id):
    msg = f"SERVER_DOWN {server_id} {int(time.time())}\n"
    for conn in index_connections:
        try:
            conn.sendall(msg.encode())
        except:
            pass


def handle_index(conn):
    index_connections.append(conn)

    try:
        while True:
            data = conn.recv(BUFFER_SIZE)
            if not data:
                break

            cmd = data.decode().strip()

            if cmd == "LIST_SERVERS":
                with lock:
                    for sid, info in servers.items():
                        line = f"SERVER {sid} {info['ip']} {info['tcp_port']} {info['load']} {info['status']}\n"
                        conn.sendall(line.encode())
                conn.sendall(b"END\n")
    finally:
        conn.close()
        index_connections.remove(conn)


def tcp_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("", TCP_PORT))
    sock.listen(5)
    print(f"🩺 Monitor TCP dinliyor: {TCP_PORT}")

    while True:
        conn, _ = sock.accept()
        threading.Thread(
            target=handle_index,
            args=(conn,),
            daemon=True
        ).start()


if __name__ == "__main__":
    threading.Thread(target=udp_listener, daemon=True).start()
    threading.Thread(target=timeout_checker, daemon=True).start()
    tcp_server()
