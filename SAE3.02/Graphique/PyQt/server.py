import socket
import threading
import subprocess
import platform
import os

class ClientHandler(threading.Thread):
    """Gère chaque connexion client dans un thread séparé."""

    def __init__(self, client_socket, client_address):
        super().__init__()
        self.client_socket = client_socket
        self.client_address = client_address
        self.python_cmd = "python3" if platform.system() != "Windows" else "python"

    def run(self):
        try:
            print(f"Connexion établie avec {self.client_address}")
            # Réception des données (type, nom, contenu)
            data = self.client_socket.recv(8192).decode()
            file_type, file_name, file_content = self.parse_data(data)

            # Sauvegarde du fichier
            self.save_file(file_name, file_content)

            # Exécution du fichier
            output = self.execute_file(file_type, file_name)

            # Envoi du résultat au client
            self.client_socket.sendall(output.encode())
        except Exception as e:
            print(f"Erreur avec {self.client_address}: {e}")
            self.client_socket.sendall(f"Erreur: {e}".encode())
        finally:
            self.client_socket.close()

    def parse_data(self, data):
        """Analyse les données reçues pour extraire le type, le nom et le contenu."""
        try:
            parts = data.split("\n", 2)
            file_type = parts[0].strip()
            file_name = parts[1].strip()
            file_content = parts[2]
            return file_type, file_name, file_content
        except Exception as e:
            raise ValueError("Données mal formatées reçues du client.")

    def save_file(self, file_name, file_content):
        """Sauvegarde le contenu dans un fichier local."""
        with open(file_name, "w") as f:
            f.write(file_content)

    def execute_file(self, file_type, file_name):
        """Exécute le fichier selon son type."""
        try:
            if file_type.lower() == "python":
                return self.run_command([self.python_cmd, file_name])
            elif file_type.lower() == "c":
                compiled_name = file_name.replace(".c", "")
                compile_result = self.run_command(["gcc", file_name, "-o", compiled_name])
                if compile_result:  # Si compilation échoue
                    return compile_result
                return self.run_command([f"./{compiled_name}"])
            elif file_type.lower() == "java":
                class_name = file_name.replace(".java", "")
                compile_result = self.run_command(["javac", file_name])
                if compile_result:  # Si compilation échoue
                    return compile_result
                return self.run_command(["java", class_name])
            else:
                return f"Type de fichier non pris en charge : {file_type}"
        finally:
            # Nettoyage des fichiers temporaires
            if os.path.exists(file_name):
                os.remove(file_name)

    def run_command(self, command):
        """Exécute une commande shell et retourne le résultat ou l'erreur."""
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                return result.stdout
            else:
                return result.stderr
        except subprocess.TimeoutExpired:
            return "Erreur: L'exécution a dépassé le temps limite."
        except Exception as e:
            return f"Erreur lors de l'exécution : {e}"

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
