import socket
import threading
import subprocess
import platform

class SlaveServer:
    def __init__(self, master_host="127.0.0.1", master_port=10000):
        self.master_host = master_host
        self.master_port = master_port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Détection de la commande Python
        self.python_cmd = "python3" if platform.system() != "Windows" else "python"

    def connect_to_master(self):
        try:
            self.socket.connect((self.master_host, self.master_port))
            print("[SLAVE] Connecté au serveur maître.")
        except Exception as e:
            print(f"[SLAVE] Erreur de connexion au maître : {e}")
            return False
        return True

    def start(self):
        while True:
            try:
                # Recevoir une tâche du maître
                code = self.socket.recv(4096).decode()
                if not code:
                    continue

                print("[SLAVE] Code reçu pour exécution.")
                result = self.execute_code(code)

                # Envoyer le résultat au maître
                self.socket.sendall(result.encode())
            except Exception as e:
                print(f"[SLAVE] Erreur lors du traitement : {e}")
                break

    def execute_code(self, code):
        try:
            # Exécuter le code avec subprocess
            result = subprocess.run(
                [self.python_cmd, "-c", code],
                capture_output=True,
                text=True,
                timeout=5
            )
            # Retourner le stdout ou stderr
            return result.stdout if result.returncode == 0 else result.stderr
        except subprocess.TimeoutExpired:
            return "Erreur : L'exécution du code a dépassé le temps limite."
        except Exception as e:
            return f"Erreur lors de l'exécution du code : {e}"

if __name__ == "__main__":
    slave = SlaveServer(master_host="127.0.0.1", master_port=10000)
    if slave.connect_to_master():
        slave.start()
