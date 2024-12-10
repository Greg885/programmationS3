import socket
import threading
import sys
import platform

class SlaveServer:
    def __init__(self, port):
        self.host = "127.0.0.1"
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.connect((self.host, self.port))

    def handle_task(self):
        try:
            print(f"Connecté au maître {self.host}:{self.port}")
            message = "Esclave prêt à traiter des tâches."
            self.server_socket.sendall(message.encode())
            data = self.server_socket.recv(4096).decode()
            print(f"Réponse du maître : {data}")
        except Exception as e:
            print(f"Erreur esclave : {e}")
        finally:
            self.server_socket.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage : python3 slave.py <master_port>")
        sys.exit(1)

    master_port = int(sys.argv[1])
    slave = SlaveServer(port=master_port)
    slave.handle_task()
