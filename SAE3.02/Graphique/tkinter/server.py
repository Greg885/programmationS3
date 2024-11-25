import socket
import threading
import subprocess
import os


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
            data = self.client_socket.recv(8192).decode()
            if not data:
                return

            # Extraction du type de fichier, du nom, et du contenu
            file_type, file_name, file_content = data.split("\n", 2)
            print(f"Type de fichier reçu : {file_type}, Nom du fichier : {file_name}")

            # Sauvegarder le fichier temporairement
            output = self.compile_and_execute(file_type, file_name, file_content)
            self.client_socket.sendall(output.encode())
        except Exception as e:
            print(f"Erreur avec {self.client_address}: {e}")
            self.client_socket.sendall(f"Erreur : {e}".encode())
        finally:
            self.client_socket.close()

    def compile_and_execute(self, file_type, file_name, file_content):
        """Compile et exécute un fichier basé sur son type."""
        try:
            if file_type == "Python":
                # Sauvegarder le fichier Python
                temp_file = "temp.py"
                with open(temp_file, "w") as file:
                    file.write(file_content)

                # Exécuter le fichier Python
                result = subprocess.run(
                    ["python3", temp_file], capture_output=True, text=True
                )

            elif file_type == "C":
                # Sauvegarder le fichier C
                temp_file = "temp.c"
                output_file = "temp.out"
                with open(temp_file, "w") as file:
                    file.write(file_content)

                # Compiler le fichier C
                compile_result = subprocess.run(
                    ["gcc", temp_file, "-o", output_file],
                    capture_output=True,
                    text=True,
                )
                if compile_result.returncode != 0:
                    return compile_result.stderr

                # Exécuter l'exécutable compilé
                result = subprocess.run([f"./{output_file}"], capture_output=True, text=True)

            elif file_type == "Java":
                # Sauvegarder le fichier Java
                temp_file = f"{file_name}.java"
                with open(temp_file, "w") as file:
                    file.write(file_content)

                # Compiler le fichier Java
                compile_result = subprocess.run(
                    ["javac", temp_file], capture_output=True, text=True
                )
                if compile_result.returncode != 0:
                    return compile_result.stderr

                # Exécuter le fichier compilé
                result = subprocess.run(
                    ["java", file_name], capture_output=True, text=True
                )

            else:
                return f"Type de fichier non supporté : {file_type}"

            # Retourner le résultat de l'exécution
            return result.stdout if result.returncode == 0 else result.stderr
        except Exception as e:
            return f"Erreur lors de l'exécution : {e}"
        finally:
            # Nettoyer les fichiers temporaires
            self.cleanup_temp_files()

    def cleanup_temp_files(self):
        """Supprime les fichiers temporaires générés."""
        for temp_file in ["temp.py", "temp.c", "temp.out", "Temp.java", "Temp.class"]:
            if os.path.exists(temp_file):
                os.remove(temp_file)


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
                print(f"Nouvelle connexion : {client_address}")
                handler = ClientHandler(client_socket, client_address)
                handler.start()
        except KeyboardInterrupt:
            print("Arrêt du serveur.")
        finally:
            self.server_socket.close()


if __name__ == "__main__":
    server = Server()
    server.start()
