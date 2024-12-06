import socket
import threading
import sys

class SlaveServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"Serveur esclave démarré sur {self.host}:{self.port}")

    def handle_client(self, client_socket):
        try:
            data = client_socket.recv(8192).decode()
            response = f"Requête traitée par un esclave : {data}"
            client_socket.sendall(response.encode())
        except Exception as e:
            print(f"Erreur lors du traitement : {e}")
        finally:
            client_socket.close()

    def start(self):
        try:
            while True:
                client_socket, client_address = self.server_socket.accept()
                threading.Thread(target=self.handle_client, args=(client_socket,)).start()
        except KeyboardInterrupt:
            print("Arrêt du serveur esclave.")
        finally:
            self.server_socket.close()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python slave_server.py <host> <port>")
        sys.exit(1)

    host = sys.argv[1]
    port = int(sys.argv[2])
    slave = SlaveServer(host, port)
    slave.start()
