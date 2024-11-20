import socket
import threading
import queue
import psutil  # Pour surveiller la charge CPU

class MasterServer:
    def __init__(self, host="127.0.0.1", port=10000, max_tasks=5):
        self.host = host
        self.port = port
        self.max_tasks = max_tasks
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"[MASTER] Serveur maître démarré sur {self.host}:{self.port}")
        
        self.task_queue = queue.Queue()
        self.slave_connections = []  # Liste des serveurs esclaves connectés
        self.lock = threading.Lock()  # Pour protéger les accès partagés

    def start(self):
        threading.Thread(target=self.handle_new_slaves, daemon=True).start()
        threading.Thread(target=self.dispatch_tasks, daemon=True).start()

        print("[MASTER] En attente de connexions clients...")
        while True:
            client_socket, client_address = self.server_socket.accept()
            threading.Thread(target=self.handle_client, args=(client_socket, client_address)).start()

    def handle_new_slaves(self):
        print("[MASTER] En attente de connexions esclaves...")
        while True:
            slave_socket, slave_address = self.server_socket.accept()
            with self.lock:
                self.slave_connections.append(slave_socket)
            print(f"[MASTER] Esclave connecté depuis {slave_address}")

    def handle_client(self, client_socket, client_address):
        print(f"[MASTER] Connexion client depuis {client_address}")
        try:
            # Recevoir le code du client
            code = client_socket.recv(4096).decode()
            if not code:
                return

            print(f"[MASTER] Code reçu du client : {client_address}")

            # Ajouter la tâche à la file d'attente
            self.task_queue.put((code, client_socket))
        except Exception as e:
            print(f"[MASTER] Erreur avec le client {client_address} : {e}")
        finally:
            client_socket.close()

    def dispatch_tasks(self):
        while True:
            if not self.task_queue.empty() and self.slave_connections:
                code, client_socket = self.task_queue.get()

                with self.lock:
                    slave_socket = self.get_least_loaded_slave()

                try:
                    # Envoyer le code à l'esclave
                    slave_socket.sendall(code.encode())
                    result = slave_socket.recv(4096).decode()

                    # Envoyer le résultat au client
                    client_socket.sendall(result.encode())
                except Exception as e:
                    print(f"[MASTER] Erreur lors de l'envoi au client : {e}")

    def get_least_loaded_slave(self):
        # Utilise psutil pour surveiller la charge et retourne le socket le moins chargé
        return min(self.slave_connections, key=lambda s: psutil.cpu_percent())

if __name__ == "__main__":
    server = MasterServer(host="127.0.0.1", port=10000, max_tasks=5)
    server.start()
