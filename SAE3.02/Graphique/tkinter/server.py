import socket
import threading
import subprocess
import platform

class ClientHandler(threading.Thread):
    """Gère chaque connexion client dans un thread séparé."""

    def __init__(self, client_socket, client_address):
        super().__init__()
        self.client_socket = client_socket
        self.client_address = client_address
        # Détection de la commande Python en fonction du système d'exploitation
        self.python_cmd = "python3" if platform.system() != "Windows" else "python"

    def run(self):
        try:
            print(f"Connexion établie avec {self.client_address}")
            # Réception du code du client
            code = self.client_socket.recv(4096).decode()

            # Exécution du code
            output = self.execute_code(code)

            # Envoi du résultat ou de l'erreur au client
            self.client_socket.sendall(output.encode())
        except Exception as e:
            print(f"Erreur avec {self.client_address}: {e}")
        finally:
            # Fermeture de la connexion
            self.client_socket.close()

    def execute_code(self, code):
        """Exécute le code Python et retourne le résultat ou l'erreur."""
        try:
            # Exécuter le code avec subprocess
            result = subprocess.run(
                [self.python_cmd, "-c", code],
                capture_output=True,
                text=True,
                timeout=5
            )
            # Retourner le stdout s'il n'y a pas d'erreurs, sinon stderr
            if result.returncode == 0:
                return result.stdout
            else:
                return result.stderr
        except subprocess.TimeoutExpired:
            return "Erreur: L'exécution du code a dépassé le temps limite."
        except Exception as e:
            return f"Erreur lors de l'exécution du code: {e}"

class Server:
    """Serveur principal qui accepte les connexions des clients."""

    def __init__(self, host="127.0.0.1", port=10000):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"Serveur démarré sur {self.host}:{self.port}")

    def start(self):
        """Démarre le serveur et accepte les connexions en continu."""
        try:
            while True:
                print("En attente de nouvelles connexions...")
                client_socket, client_address = self.server_socket.accept()
                # Création d'un thread pour chaque client
                handler = ClientHandler(client_socket, client_address)
                handler.start()
        except KeyboardInterrupt:
            print("Serveur arrêté.")
        finally:
            self.server_socket.close()

# Lancer le serveur
if __name__ == "__main__":
    server = Server(host="127.0.0.1", port=10000)
    server.start()
