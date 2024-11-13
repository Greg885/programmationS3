import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import socket
import threading


class ConnectionManager:
    """Gère la connexion et l'envoi de données au serveur."""

    def __init__(self, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = server_port
        self.client_socket = None

    def connect(self):
        """Établit une connexion au serveur."""
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.server_ip, self.server_port))
            return True
        except socket.error as e:
            messagebox.showerror("Erreur de connexion", f"Impossible de se connecter au serveur : {e}")
            return False

    def send_code(self, code):
        """Envoie le code modifié dans l'éditeur au serveur."""
        try:
            self.client_socket.sendall(code.encode())
            return True
        except Exception as e:
            messagebox.showerror("Erreur d'envoi", f"Erreur lors de l'envoi du code : {e}")
            return False

    def receive_response(self):
        """Reçoit la réponse du serveur."""
        try:
            response = self.client_socket.recv(4096).decode()
            return response
        except Exception as e:
            messagebox.showerror("Erreur de réception", f"Erreur lors de la réception des données : {e}")
            return None

    def close_connection(self):
        """Ferme la connexion au serveur."""
        if self.client_socket:
            self.client_socket.close()


class ClientApp:
    """Interface graphique pour le client."""

    def __init__(self, root):
        self.root = root
        self.root.title("Client de Connexion au Serveur")
        self.root.geometry("600x600")
        self.root.configure(bg="#f0f0f5")

        # Paramètres par défaut
        self.default_ip = "127.0.0.1"
        self.default_port = 10000

        # Variables de l'interface
        self.server_ip_var = tk.StringVar(value=self.default_ip)
        self.server_port_var = tk.IntVar(value=self.default_port)
        self.filepath = None

        # Création des widgets
        self.create_widgets()

    def create_widgets(self):
        """Crée les éléments de l'interface graphique."""
        title_label = ttk.Label(self.root, text="Connexion au Serveur", font=("Helvetica", 16, "bold"),
                                background="#f0f0f5")
        title_label.pack(pady=10)

        connection_frame = ttk.Frame(self.root)
        connection_frame.pack(pady=5)

        ip_label = ttk.Label(connection_frame, text="Adresse IP :", font=("Arial", 12))
        ip_label.grid(row=0, column=0, padx=5, pady=5)
        ip_entry = ttk.Entry(connection_frame, textvariable=self.server_ip_var, font=("Arial", 12), width=15)
        ip_entry.grid(row=0, column=1, padx=5, pady=5)

        port_label = ttk.Label(connection_frame, text="Port :", font=("Arial", 12))
        port_label.grid(row=1, column=0, padx=5, pady=5)
        port_entry = ttk.Entry(connection_frame, textvariable=self.server_port_var, font=("Arial", 12), width=15)
        port_entry.grid(row=1, column=1, padx=5, pady=5)

        load_button = ttk.Button(self.root, text="Charger un fichier Python", command=self.load_file)
        load_button.pack(pady=5)

        editor_label = ttk.Label(self.root, text="Éditeur de fichier :", font=("Arial", 12))
        editor_label.pack(pady=5)
        self.editor_text = tk.Text(self.root, height=15, width=70, bg="#e8e8f0", font=("Courier", 10))
        self.editor_text.pack(pady=5)

        send_button = ttk.Button(self.root, text="Envoyer le code au serveur", command=self.send_to_server)
        send_button.pack(pady=10)

        result_label = ttk.Label(self.root, text="Résultat d'exécution :", font=("Arial", 12))
        result_label.pack(pady=5)
        self.result_text = tk.Text(self.root, height=10, width=70, state="disabled", bg="#e8e8f0", font=("Courier", 10))
        self.result_text.pack(pady=10)

    def load_file(self):
        """Charge un fichier Python à envoyer au serveur et affiche son contenu dans l'éditeur."""
        self.filepath = filedialog.askopenfilename(filetypes=[("Python Files", "*.py")])
        if self.filepath:
            with open(self.filepath, 'r') as file:
                code = file.read()
                self.editor_text.delete(1.0, tk.END)
                self.editor_text.insert(tk.END, code)
            messagebox.showinfo("Fichier chargé", f"Fichier sélectionné : {self.filepath}")

    def send_to_server(self):
        """Envoie le code modifié de l'éditeur au serveur."""
        code = self.editor_text.get(1.0, tk.END)
        server_ip = self.server_ip_var.get()
        server_port = self.server_port_var.get()
        connection_manager = ConnectionManager(server_ip, server_port)

        if connection_manager.connect():
            if connection_manager.send_code(code):
                threading.Thread(target=self.receive_response, args=(connection_manager,)).start()

    def receive_response(self, connection_manager):
        """Reçoit la réponse du serveur et l'affiche dans l'interface."""
        response = connection_manager.receive_response()
        if response:
            self.display_result(response)
        connection_manager.close_connection()

    def display_result(self, result):
        """Affiche le résultat dans la zone de texte des résultats."""
        self.result_text.config(state="normal")
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, result)
        self.result_text.config(state="disabled")


class LoginWindow:
    """Fenêtre de connexion avec mot de passe."""

    def __init__(self, root):
        self.root = root
        self.root.title("Authentification")
        self.root.geometry("300x150")

        self.password_var = tk.StringVar()

        ttk.Label(root, text="Mot de passe :", font=("Arial", 12)).pack(pady=10)
        self.password_entry = ttk.Entry(root, textvariable=self.password_var, show="*", font=("Arial", 12))
        self.password_entry.pack(pady=5)

        ttk.Button(root, text="Connexion", command=self.check_password).pack(pady=10)
        self.password_entry.focus()

    def check_password(self):
        """Vérifie le mot de passe entré par l'utilisateur."""
        if self.password_var.get() == "toto":  # Remplacez par le mot de passe souhaité
            self.root.destroy()
            main_window = tk.Tk()
            app = ClientApp(main_window)
            main_window.mainloop()
        else:
            messagebox.showerror("Erreur", "Mot de passe incorrect")


# Lancement de la fenêtre de connexion
if __name__ == "__main__":
    root = tk.Tk()
    login_app = LoginWindow(root)
    root.mainloop()
