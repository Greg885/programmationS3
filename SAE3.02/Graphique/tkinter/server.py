import socket
import threading
import subprocess
import platform


class ClientHandler(threading.Thread):
    """Gère chaque connexion client."""

    def __init__(self, client_socket, client_address):
        super().__init__()
        self.client_socket = client_socket
        self.client_address = client_address

    def run(self):
        try:
            print(f"Connexion établie avec {self.client_address}")

            # Réception des données du client
            data = self.client_socket.recv(4096).decode()
            if not data:
                return

            # Extraction du type et du code
            code_type, code = data.split("\n", 1)
            print(f"Type de code reçu: {code_type}")

            # Exécution du code
            output = self.execute_code(code, code_type)
            self.client_socket.sendall(output.encode())
        except Exception as e:
            print(f"Erreur avec {self.client_address}: {e}")
        finally:
            self.client_socket.close()

    def execute_code(self, code, code_type):
        """Exécute le code et retourne le résultat."""
        command = "python3" if code_type == "Python" else "gcc"
        try:
            if code_type == "Python":
                result = subprocess.run(
                    ["python3", "-c", code],
                    capture_output=True,
                    text=True,
                )
            elif code_type == "C":
                # Sauvegarde temporaire et compilation
                with open("temp.c", "w") as file:
                    file.write(code)
                result = subprocess.run(
                    ["gcc", "temp.c", "-o", "temp.out"], capture_output=True, text=True
                )
                if result.returncode == 0:
                    result = subprocess.run(
                        ["./temp.out"], capture_output=True, text=True
                    )
            return result.stdout if result.returncode == 0 else result.stderr
        except Exception as e:
            return f"Erreur lors de l'exécution : {e}"


class Server:
    """Serveur principal."""

    def __init__(self, host="127.0.0.1", port=10000):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((host, port))
        self.server_socket.listen(5)
        print(f"Serveur en écoute sur {host}:{port}")

    def start(self):
        """Démarre le serveur."""
        try:
            while True:
                client_socket, client_address = self.server_socket.accept()
                print(f"Nouvelle connexion: {client_address}")
                handler = ClientHandler(client_socket, client_address)
                handler.start()
        except KeyboardInterrupt:
            print("Arrêt du serveur.")
        finally:
            self.server_socket.close()


if __name__ == "__main__":
    server = Server()
    server.start()
