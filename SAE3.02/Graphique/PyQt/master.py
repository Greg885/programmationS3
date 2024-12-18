# Script master.py codé par G.Runser pour la SAE3.02
# Si vous souhaitez créer du Low-Balancing veuillez vous référer au document d'installation ou au fichier README
# Code commenté - Plus d'informations sur le document de réponse

import sys
import socket
import threading
import subprocess
import platform
import os
from queue import Queue
import psutil
import uuid

# Classe gérant la communication avec un client connecté
class SlaveHandler(threading.Thread):
    def __init__(self, client_socket, client_address, server):
        super().__init__()
        self.client_socket = client_socket
        self.client_address = client_address
        self.server = server
        self.python_cmd = "python3" if platform.system() != "Windows" else "python"  # Commande Python selon l'OS
        self.running = True

    # Fonction principale pour traiter les tâches reçues du client
    def run(self):
        try:
            print(f"Connexion établie avec {self.client_address}")
            data = self.client_socket.recv(4096).decode()  # Réception des données
            response = self.handle_task(data)  # Traitement de la tâche
            self.client_socket.sendall(response.encode())  # Renvoi de la réponse au client
        except Exception as e:
            print(f"Erreur avec {self.client_address}: {e}")
        finally:
            self.client_socket.close()  # Fermeture de la connexion avec le client
            self.server.decrement_task_count()  # Décrémentation du compteur des tâches actives

    # Gère le traitement des données reçues
    def handle_task(self, data):
        try:
            if data == "CPU_USAGE":  # Demande d'utilisation CPU
                cpu_usage = self.get_current_process_cpu_usage()
                return f"CPU Usage: {cpu_usage}%"
            else:  # Traitement des fichiers
                return self.handle_file(data)
        except Exception as e:
            return f"Erreur lors du traitement : {e}"

    # Gère les fichiers reçus (Python, Java, C, etc.)
    def handle_file(self, data):
        try:
            file_type, file_name, file_content = data.split("\n", 2)  # Extraction des données
            print(f"Fichier reçu : {file_name}, Type : {file_type}")
            unique_id = uuid.uuid4().hex  # Génération d'un identifiant unique
            temp_filename = f"temp_{unique_id}_{file_name}"  # Nom temporaire pour le fichier
            with open(temp_filename, "w") as temp_file:
                temp_file.write(file_content)

            # Appel de l'exécution selon le type de fichier
            if file_type.lower() == "python":
                return self.execute_python(temp_filename)

            elif file_type.lower() == "java":
                return self.execute_java(temp_filename)

            elif file_type.lower() == "c":
                return self.execute_c(temp_filename)

            else:
                return f"Type de fichier non supporté : {file_type}"
        except Exception as e:
            return f"Erreur lors du traitement du fichier : {e}"

    # Exécute les scripts Python
    def execute_python(self, filename):
        try:
            result = subprocess.run(
                [self.python_cmd, filename],  # Exécute le script Python
                capture_output=True,
                text=True,
            )
            os.remove(filename)  # Supprime le fichier temporaire
            return result.stdout if result.returncode == 0 else result.stderr
        except Exception as e:
            return f"Erreur lors de l'exécution Python : {e}"

    # Compile et exécute les fichiers Java
    def execute_java(self, filename):
        try:
            compiled_filename = filename.replace(".java", ".class")
            compile_result = subprocess.run(
                ["javac", filename],  # Compilation du fichier Java
                capture_output=True,
                text=True,
            )
            if compile_result.returncode == 0:  # Si la compilation réussit
                execute_result = subprocess.run(
                    ["java", filename.replace(".java", "")],  # Exécution du fichier compilé
                    capture_output=True,
                    text=True,
                )
                os.remove(filename)  # Suppression des fichiers temporaires
                os.remove(compiled_filename)
                return execute_result.stdout if execute_result.returncode == 0 else execute_result.stderr
            else:
                os.remove(filename)
                return compile_result.stderr
        except Exception as e:
            return f"Erreur lors de l'exécution Java : {e}"

    # Compile et exécute les fichiers C
    def execute_c(self, filename):
        try:
            compiled_filename = filename.replace(".c", ".out")
            compile_result = subprocess.run(
                ["gcc", filename, "-o", compiled_filename],  # Compilation du fichier C
                capture_output=True,
                text=True,
            )
            if compile_result.returncode == 0:  # Si la compilation réussit
                execute_result = subprocess.run(
                    [f"./{compiled_filename}"],  # Exécution du fichier compilé
                    capture_output=True,
                    text=True,
                )
                os.remove(filename)  # Suppression des fichiers temporaires
                os.remove(compiled_filename)
                return execute_result.stdout if execute_result.returncode == 0 else execute_result.stderr
            else:
                os.remove(filename)
                return compile_result.stderr
        except Exception as e:
            return f"Erreur lors de l'exécution C : {e}"

    # Retourne l'utilisation actuelle du CPU par le processus
    @staticmethod
    def get_current_process_cpu_usage():
        process = psutil.Process()
        return process.cpu_percent(interval=1)


# Classe représentant le serveur maître
class MasterServer:
    def __init__(self, max_concurrent_tasks, slave_ips, host="", port=10000):
        self.max_concurrent_tasks = max_concurrent_tasks  # Nombre max de tâches simultanées
        self.current_task_count = 0  # Compteur des tâches actives
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Configuration du socket
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)  # Le serveur écoute jusqu'à 5 connexions
        self.is_running = threading.Event()
        self.is_running.set()
        self.slave_ips = slave_ips  # Liste des esclaves pour le load balancing
        self.task_queue = Queue()
        print(f"Serveur maître démarré sur {self.host}:{self.port}, max_concurrent_tasks={self.max_concurrent_tasks}")

    # Démarre le serveur pour accepter les connexions entrantes
    def start(self):
        try:
            while self.is_running.is_set():
                self.server_socket.settimeout(1.0)
                try:
                    client_socket, client_address = self.server_socket.accept()
                    if self.current_task_count >= self.max_concurrent_tasks:  # Vérifie si la limite est atteinte
                        print(f"Nombre de tâches simultanées atteint ({self.current_task_count}), redirection vers un esclave...")
                        self.redirect_to_slave(client_socket, client_address)
                    else:
                        self.increment_task_count()
                        handler = SlaveHandler(client_socket, client_address, self)
                        handler.start()
                except socket.timeout:
                    continue
        except KeyboardInterrupt:
            print("Arrêt demandé par l'utilisateur.")
        finally:
            self.stop()

    # Redirige la tâche vers un esclave disponible
    def redirect_to_slave(self, client_socket, client_address):
        if not self.slave_ips:  # Si aucun esclave n'est disponible
            print("Aucun esclave disponible pour rediriger la tâche.")
            client_socket.close()
            return

        for slave_ip, slave_port in self.slave_ips:  # Parcourt les esclaves
            try:
                print(f"Tentative de redirection vers l'esclave {slave_ip}:{slave_port}...")
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as slave_socket:
                    slave_socket.connect((slave_ip, slave_port))
                    data = client_socket.recv(4096)  # Réception des données du client
                    slave_socket.sendall(data)  # Envoi des données à l'esclave
                    response = slave_socket.recv(4096)  # Réception de la réponse de l'esclave
                    client_socket.sendall(response)  # Renvoi de la réponse au client
                print(f"Tâche redirigée avec succès vers l'esclave {slave_ip}:{slave_port}.")
                break
            except Exception as e:
                print(f"Erreur avec l'esclave {slave_ip}:{slave_port} : {e}")
        else:
            print("Impossible de rediriger la tâche vers un esclave.")
            client_socket.close()

    # Incrémente le compteur de tâches
    def increment_task_count(self):
        self.current_task_count += 1
        print(f"Nombre de tâches simultanées : {self.current_task_count}")

    # Décrémente le compteur de tâches
    def decrement_task_count(self):
        self.current_task_count -= 1
        print(f"Nombre de tâches simultanées : {self.current_task_count}")

    # Arrête le serveur
    def stop(self):
        self.is_running.clear()
        self.server_socket.close()
        print("Serveur arrêté proprement.")


# Point d'entrée du script
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage : python3 master.py <max_concurrent_tasks>")
        sys.exit(1)

    max_concurrent_tasks = int(sys.argv[1])  # Nombre max de tâches simultanées
    slave_ips = [("127.0.0.1", 10001), ("127.0.0.1", 10002)]  # Liste des esclaves (<----- REMPLIR ICI)

    server = MasterServer(max_concurrent_tasks=max_concurrent_tasks, slave_ips=slave_ips)
    server.start()
