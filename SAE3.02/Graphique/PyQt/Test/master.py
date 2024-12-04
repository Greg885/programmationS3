import socket
import threading
import os
import platform
import subprocess
import psutil


class SlaveHandler(threading.Thread):
    def __init__(self, client_socket, client_address):
        super().__init__()
        self.client_socket = client_socket
        self.client_address = client_address
        self.python_cmd = "python3" if platform.system() != "Windows" else "python"

    def run(self):
        try:
            print(f"Connexion établie avec {self.client_address}")
            data = self.client_socket.recv(4096).decode()

            if data == "CPU_USAGE":
                cpu_usage = psutil.cpu_percent()
                self.client_socket.sendall(f"{cpu_usage}".encode())
            else:
                response = self.handle_file(data)
                self.client_socket.sendall(response.encode())
        except Exception as e:
            print(f"Erreur avec {self.client_address}: {e}")
        finally:
            self.client_socket.close()

    def handle_file(self, data):
        try:
            file_type, file_name, file_content = data.split("\n", 2)

            # Enregistrer temporairement le fichier
            temp_filename = f"temp_{file_name}"
            with open(temp_filename, "w") as temp_file:
                temp_file.write(file_content)

            # Exécuter le fichier si Python
            if file_type.lower() == "python":
                result = subprocess.run(
                    [self.python_cmd, temp_filename],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                os.remove(temp_filename)  # Supprimer après exécution
                if result.returncode == 0:
                    return result.stdout
                else:
                    return result.stderr
            else:
                return f"Type de fichier non supporté : {file_type}"
        except Exception as e:
            return f"Erreur lors du traitement du fichier : {e}"


class MasterServer:
    def __init__(self, host="127.0.0.1", port=10000):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"Serveur maître démarré sur {self.host}:{self.port}")

    def start(self):
        try:
            while True:
                client_socket, client_address = self.server_socket.accept()
                handler = SlaveHandler(client_socket, client_address)
                handler.start()
        except KeyboardInterrupt:
            print("Serveur arrêté.")
        finally:
            self.server_socket.close()


if __name__ == "__main__":
    server = MasterServer(host="127.0.0.1", port=10000)
    server.start()
