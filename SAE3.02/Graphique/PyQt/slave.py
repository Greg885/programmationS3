#Script slave.py codé par G.Runser pour la SAE3.02
#Si vous souhaitez créer du Low-Balancing veuillez vous réferer au document d'installation ou au fichier README

import sys
import socket
import threading
import subprocess
import platform
import os
import uuid

class SlaveServer:
    def __init__(self, host="127.0.0.1", port=10001): #Modification pour chaque slave
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        self.is_running = threading.Event()
        self.is_running.set()
        print(f"Serveur esclave démarré sur {self.host}:{self.port}")

    def start(self):
        try:
            while self.is_running.is_set():
                client_socket, client_address = self.server_socket.accept()
                print(f"Connexion reçue de {client_address}")
                handler = SlaveHandler(client_socket)
                handler.start()
        except KeyboardInterrupt:
            print("Arrêt demandé par l'utilisateur.")
        finally:
            self.stop()

    def stop(self):
        self.is_running.clear()
        self.server_socket.close()
        print("Serveur esclave arrêté proprement.")


class SlaveHandler(threading.Thread):
    def __init__(self, client_socket):
        super().__init__()
        self.client_socket = client_socket
        self.python_cmd = "python3" if platform.system() != "Windows" else "python"

    def run(self):
        try:
            data = self.client_socket.recv(4096).decode()
            if not data:
                print("Aucune donnée reçue.")
                return

            response = self.handle_task(data)
            self.client_socket.sendall(response.encode())
        except Exception as e:
            print(f"Erreur lors du traitement de la tâche : {e}")
            self.client_socket.sendall(f"Erreur : {e}".encode())
        finally:
            self.client_socket.close()

    def handle_task(self, data):
        try:
            file_type, file_name, file_content = data.split("\n", 2)
            print(f"Tâche reçue : {file_name}, Type : {file_type}")
            unique_id = uuid.uuid4().hex
            temp_filename = f"temp_{unique_id}_{file_name}"
            with open(temp_filename, "w") as temp_file:
                temp_file.write(file_content)

            if file_type.lower() == "python":
                return self.execute_python(temp_filename)

            elif file_type.lower() == "java":
                return self.execute_java(temp_filename)

            elif file_type.lower() == "c":
                return self.execute_c(temp_filename)

            else:
                return f"Type de fichier non supporté : {file_type}"
        except Exception as e:
            return f"Erreur lors du traitement : {e}"

    def execute_python(self, filename):
        try:
            result = subprocess.run(
                [self.python_cmd, filename],
                capture_output=True,
                text=True,
            )
            os.remove(filename)
            return result.stdout if result.returncode == 0 else result.stderr
        except Exception as e:
            return f"Erreur lors de l'exécution Python : {e}"

    def execute_java(self, filename):
        try:
            compiled_filename = filename.replace(".java", ".class")
            compile_result = subprocess.run(
                ["javac", filename],
                capture_output=True,
                text=True,
            )
            if compile_result.returncode == 0:
                execute_result = subprocess.run(
                    ["java", filename.replace(".java", "")],
                    capture_output=True,
                    text=True,
                )
                os.remove(filename)
                os.remove(compiled_filename)
                return execute_result.stdout if execute_result.returncode == 0 else execute_result.stderr
            else:
                os.remove(filename)
                return compile_result.stderr
        except Exception as e:
            return f"Erreur lors de l'exécution Java : {e}"

    def execute_c(self, filename):
        try:
            compiled_filename = filename.replace(".c", ".out")
            compile_result = subprocess.run(
                ["gcc", filename, "-o", compiled_filename],
                capture_output=True,
                text=True,
            )
            if compile_result.returncode == 0:
                execute_result = subprocess.run(
                    [f"./{compiled_filename}"],
                    capture_output=True,
                    text=True,
                )
                os.remove(filename)
                os.remove(compiled_filename)
                return execute_result.stdout if execute_result.returncode == 0 else execute_result.stderr
            else:
                os.remove(filename)
                return compile_result.stderr
        except Exception as e:
            return f"Erreur lors de l'exécution C : {e}"


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage : python3 slave.py <port>")
        sys.exit(1)

    port = int(sys.argv[1])
    slave_server = SlaveServer(port=port)
    slave_server.start()
