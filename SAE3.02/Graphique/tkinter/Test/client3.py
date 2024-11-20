import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import socket
import threading


class ConnectionManager:
    """Gère la connexion et l'envoi de données au serveur."""

    def __init__(self):
        self.server_ip = None
        self.server_port = None

    def set_server_info(self, server_ip, server_port):
        """Définit les informations du serveur."""
        self.server_ip = server_ip
        self.server_port = server_port

    def test_connection(self):
        """Teste la connexion au serveur."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as test_socket:
                test_socket.settimeout(5)  # Temps limite de connexion
                test_socket.connect((self.server_ip, self.server_port))
            return True
        except (socket.timeout, socket.error) as e:
            return f"Erreur de connexion : {e}"

    def send_code(self, code, code_type):
        """Crée une nouvelle connexion, envoie le code et reçoit la réponse."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                client_socket.connect((self.server_ip, self.server_port))
                client_socket.sendall(f"{code_type}\n{code}".encode())
                response = client_socket.recv(4096).decode()
                return response
        except Exception as e:
            return f"Erreur lors de l'envoi : {e}"


class ClientApp:
    """Interface graphique pour le client."""

    def __init__(self, root):
        self.root = root
        self.root.title("Client Serveur Futuriste")
        self.root.configure(bg="#1e1e2f")  # Couleur de fond sombre
        self.connection_manager = ConnectionManager()

        # Appliquer des styles futuristes
        self.style = ttk.Style()
        self.apply_futuristic_styles()

        # Création des interfaces
        self.create_connection_interface()

    def apply_futuristic_styles(self):
        """Applique un thème futuriste."""
        self.style.theme_use("clam")

        # Style des boutons
        self.style.configure(
            "TButton",
            font=("Consolas", 12),
            foreground="#0ef9f9",
            background="#262640",
            borderwidth=1,
            padding=5,
        )
        self.style.map(
            "TButton",
            background=[("active", "#0ef9f9")],
            foreground=[("active", "#1e1e2f")],
        )

        # Style des étiquettes
        self.style.configure(
            "TLabel",
            font=("Consolas", 12),
            foreground="#0ef9f9",
            background="#1e1e2f",
        )

        # Style des entrées
        self.style.configure(
            "TEntry",
            font=("Consolas", 12),
            fieldbackground="#262640",
            foreground="#0ef9f9",
            bordercolor="#0ef9f9",
        )

        # Style des boîtes de texte
        self.style.configure(
            "Text",
            font=("Courier New", 10),
            background="#262640",
            foreground="#0ef9f9",
            borderwidth=1,
            relief="flat",
        )

    def create_connection_interface(self):
        """Crée l'interface pour la connexion au serveur."""
        self.clear_root()
        self.root.geometry("500x300")

        ttk.Label(self.root, text="Adresse IP du serveur:", style="TLabel").pack(pady=10)
        self.server_ip_var = tk.StringVar(value="127.0.0.1")
        ttk.Entry(self.root, textvariable=self.server_ip_var, style="TEntry", width=30).pack()

        ttk.Label(self.root, text="Port du serveur:", style="TLabel").pack(pady=10)
        self.server_port_var = tk.IntVar(value=10000)
        ttk.Entry(self.root, textvariable=self.server_port_var, style="TEntry", width=30).pack()

        ttk.Button(self.root, text="Se connecter", command=self.connect_to_server).pack(pady=20)

    def connect_to_server(self):
        """Teste la connexion au serveur et passe à l'interface suivante si elle réussit."""
        server_ip = self.server_ip_var.get()
        server_port = self.server_port_var.get()

        self.connection_manager.set_server_info(server_ip, server_port)
        result = self.connection_manager.test_connection()

        if result is True:
            messagebox.showinfo("Connexion réussie", f"Connecté à {server_ip}:{server_port}")
            self.create_file_interface()
        else:
            messagebox.showerror("Erreur de connexion", result)

    def create_file_interface(self):
        """Crée l'interface pour le choix et l'envoi du fichier."""
        self.clear_root()
        self.root.geometry("500x800")  # Fenêtre agrandie

        ttk.Button(self.root, text="Retour", command=self.create_connection_interface).pack(pady=5)

        ttk.Label(self.root, text="Choix du type de fichier:", style="TLabel").pack(pady=10)
        self.file_type_var = tk.StringVar(value="Python")
        ttk.Combobox(
            self.root, textvariable=self.file_type_var, values=["Python", "C"], state="readonly"
        ).pack()

        ttk.Button(self.root, text="Charger un fichier", command=self.load_file).pack(pady=10)

        self.editor_text = tk.Text(
            self.root, height=25, width=100, bg="#262640", fg="#0ef9f9", font=("Courier", 10)
        )
        self.editor_text.pack(pady=10)

        ttk.Button(self.root, text="Envoyer au serveur", command=self.send_to_server).pack(pady=10)

        ttk.Label(self.root, text="Résultat:", style="TLabel").pack(pady=5)
        self.result_text = tk.Text(
            self.root, height=15, width=100, bg="#262640", fg="#0ef9f9", font=("Courier", 10)
        )
        self.result_text.config(state="disabled")
        self.result_text.pack(pady=10)

    def clear_root(self):
        """Nettoie la fenêtre principale."""
        for widget in self.root.winfo_children():
            widget.destroy()

    def load_file(self):
        """Charge un fichier et affiche son contenu."""
        filepath = filedialog.askopenfilename(filetypes=[("Tous les fichiers", "*.*")])
        if filepath:
            with open(filepath, "r") as file:
                content = file.read()
                self.editor_text.delete(1.0, tk.END)
                self.editor_text.insert(tk.END, content)

    def send_to_server(self):
        """Envoie le fichier et son type au serveur."""
        code = self.editor_text.get(1.0, tk.END).strip()
        code_type = self.file_type_var.get()

        if code and code_type:
            threading.Thread(target=self.handle_server_response, args=(code, code_type)).start()

    def handle_server_response(self, code, code_type):
        """Gère la réponse du serveur après l'envoi du code."""
        response = self.connection_manager.send_code(code, code_type)
        self.display_result(response)

    def display_result(self, result):
        """Affiche le résultat dans la zone de texte des résultats."""
        self.result_text.config(state="normal")
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, result)
        self.result_text.config(state="disabled")


if __name__ == "__main__":
    root = tk.Tk()
    app = ClientApp(root)
    root.mainloop()
