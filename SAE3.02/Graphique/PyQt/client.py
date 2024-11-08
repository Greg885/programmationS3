import sys
import socket
import threading
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit, QLineEdit, QFileDialog, QMessageBox

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
            QMessageBox.critical(None, "Erreur de connexion", f"Impossible de se connecter au serveur : {e}")
            return False

    def send_code(self, code):
        """Envoie le code modifié au serveur."""
        try:
            self.client_socket.sendall(code.encode())
            return True
        except Exception as e:
            QMessageBox.critical(None, "Erreur d'envoi", f"Erreur lors de l'envoi du code : {e}")
            return False

    def receive_response(self):
        """Reçoit la réponse du serveur."""
        try:
            response = self.client_socket.recv(4096).decode()
            return response
        except Exception as e:
            QMessageBox.critical(None, "Erreur de réception", f"Erreur lors de la réception des données : {e}")
            return None

    def close_connection(self):
        """Ferme la connexion au serveur."""
        if self.client_socket:
            self.client_socket.close()

class ClientApp(QWidget):
    """Interface graphique pour le client."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Client de Connexion au Serveur")
        self.setGeometry(100, 100, 600, 600)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Champs IP et Port
        self.server_ip_input = QLineEdit("127.0.0.1")
        self.server_port_input = QLineEdit("10000")
        self.layout.addWidget(QLabel("Adresse IP du serveur:"))
        self.layout.addWidget(self.server_ip_input)
        self.layout.addWidget(QLabel("Port du serveur:"))
        self.layout.addWidget(self.server_port_input)

        # Bouton pour charger le fichier
        self.load_button = QPushButton("Charger un fichier Python")
        self.load_button.clicked.connect(self.load_file)
        self.layout.addWidget(self.load_button)

        # Éditeur de texte pour afficher et modifier le fichier
        self.editor = QTextEdit()
        self.editor.setPlaceholderText("Le code du fichier chargé s'affichera ici pour édition")
        self.layout.addWidget(QLabel("Éditeur de fichier:"))
        self.layout.addWidget(self.editor)

        # Bouton pour envoyer le code modifié
        self.send_button = QPushButton("Envoyer le code au serveur")
        self.send_button.clicked.connect(self.send_to_server)
        self.layout.addWidget(self.send_button)

        # Zone d'affichage des résultats
        self.result_view = QTextEdit()
        self.result_view.setReadOnly(True)
        self.layout.addWidget(QLabel("Résultat d'exécution:"))
        self.layout.addWidget(self.result_view)

    def load_file(self):
        """Charge un fichier Python à envoyer au serveur et affiche son contenu dans l'éditeur."""
        filepath, _ = QFileDialog.getOpenFileName(self, "Charger un fichier Python", "", "Python Files (*.py)")
        if filepath:
            with open(filepath, 'r') as file:
                code = file.read()
                self.editor.setText(code)

    def send_to_server(self):
        """Envoie le code modifié de l'éditeur au serveur."""
        # Récupère le code depuis l'éditeur de texte
        code = self.editor.toPlainText()
        server_ip = self.server_ip_input.text()
        server_port = int(self.server_port_input.text())
        connection_manager = ConnectionManager(server_ip, server_port)

        if connection_manager.connect():
            if connection_manager.send_code(code):
                # Attente de la réponse du serveur dans un thread séparé
                threading.Thread(target=self.receive_response, args=(connection_manager,)).start()

    def receive_response(self, connection_manager):
        """Reçoit la réponse du serveur et l'affiche dans l'interface."""
        response = connection_manager.receive_response()
        if response:
            self.result_view.setText(response)
        connection_manager.close_connection()

# Création de l'application et lancement de l'interface
app = QApplication(sys.argv)
window = ClientApp()
window.show()
sys.exit(app.exec())
