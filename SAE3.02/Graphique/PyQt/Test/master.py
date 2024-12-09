import socket
import threading
import platform
import subprocess
import psutil
import os


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
                cpu_usage = self.get_current_process_cpu_usage()
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
            print(f"Fichier reçu : {file_name}, Type : {file_type}")
            temp_filename = f"temp_{file_name}"
            with open(temp_filename, "w") as temp_file:
                temp_file.write(file_content)

            if file_type.lower() == "python":
                result = subprocess.run(
                    [self.python_cmd, temp_filename],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                os.remove(temp_filename)
                if result.returncode == 0:
                    return result.stdout
                else:
                    return result.stderr
            else:
                return f"Type de fichier non supporté : {file_type}"
        except Exception as e:
            return f"Erreur lors du traitement du fichier : {e}"

    @staticmethod
    def get_current_process_cpu_usage():
        process = psutil.Process()
        return process.cpu_percent(interval=1)  # Calculer l'utilisation du CPU pour ce processus


class MasterServer:
    def __init__(self, host="", port=10000):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        self.is_running = threading.Event()
        self.is_running.set()
        print(f"Serveur maître démarré sur {self.host}:{self.port}")

    def start(self):
        # Démarrer le thread d'écoute des commandes utilisateur
        command_thread = threading.Thread(target=self.listen_for_commands, daemon=True)
        command_thread.start()

        try:
            while self.is_running.is_set():
                self.server_socket.settimeout(1.0)  # Timeout pour éviter le blocage sur accept()
                try:
                    client_socket, client_address = self.server_socket.accept()
                    handler = SlaveHandler(client_socket, client_address)
                    handler.start()
                except socket.timeout:
                    continue  # Timeout atteint, revenir au début de la boucle
        except KeyboardInterrupt:
            print("Arrêt demandé par l'utilisateur.")
        finally:
            self.stop()

    def listen_for_commands(self):
        while self.is_running.is_set():
            command = input("Entrez 'arret' pour arrêter le serveur : ").strip()
            if command.lower() == "arret":
                self.stop()

    def stop(self):
        self.is_running.clear()
        self.server_socket.close()
        print("Serveur arrêté proprement.")


if __name__ == "__main__":
    server = MasterServer(host="", port=10000)
    try:
        server.start()
    except Exception as e:
        print(f"Erreur inattendue : {e}")
        server.stop()
