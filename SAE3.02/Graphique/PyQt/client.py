import sys
import socket
from PyQt5.QtWidgets import (
    QApplication, QWidget, QGridLayout, QPushButton, QLabel,
    QLineEdit, QTextEdit, QFileDialog, QComboBox, QMessageBox
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QThread, pyqtSignal
import os


class ConnectionManager:
    def __init__(self):
        self.server_ip = None
        self.server_port = None

    def set_server_info(self, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = server_port

    def test_connection(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as test_socket:
                test_socket.settimeout(5)
                test_socket.connect((self.server_ip, self.server_port))
            return True
        except (socket.timeout, socket.error) as e:
            return f"Erreur de connexion : {e}"

    def send_file(self, file_content, file_type, file_name):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                client_socket.connect((self.server_ip, self.server_port))
                client_socket.sendall(f"{file_type}\n{file_name}\n{file_content}".encode())
                response = client_socket.recv(4096).decode()
                return response
        except Exception as e:
            return f"Erreur lors de l'envoi : {e}"


class FileSenderThread(QThread):
    result_signal = pyqtSignal(str)

    def __init__(self, manager, file_content, file_type, file_name):
        super().__init__()
        self.manager = manager
        self.file_content = file_content
        self.file_type = file_type
        self.file_name = file_name

    def run(self):
        result = self.manager.send_file(self.file_content, self.file_type, self.file_name)
        self.result_signal.emit(result)


class ClientApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Client")
        self.connection_manager = ConnectionManager()

        self.init_ui()

    def init_ui(self):
        # Layout principal
        self.layout = QGridLayout()
        self.setLayout(self.layout)

        # Interface de connexion
        self.create_connection_interface()

    def create_connection_interface(self):
        self.clear_layout()

        self.resize(700, 300)  # Taille spécifique pour la fenêtre de connexion

        # Adresse IP
        self.layout.addWidget(QLabel("Adresse IP du serveur:"), 0, 0)
        self.server_ip_input = QLineEdit("127.0.0.1")
        self.layout.addWidget(self.server_ip_input, 0, 1)

        # Port
        self.layout.addWidget(QLabel("Port du serveur:"), 1, 0)
        self.server_port_input = QLineEdit("10000")
        self.layout.addWidget(self.server_port_input, 1, 1)

        # Bouton connexion
        connect_button = QPushButton("Se connecter")
        connect_button.clicked.connect(self.connect_to_server)
        self.layout.addWidget(connect_button, 4, 0, 1, 2)

    def connect_to_server(self):
        server_ip = self.server_ip_input.text()
        server_port = int(self.server_port_input.text())

        self.connection_manager.set_server_info(server_ip, server_port)
        result = self.connection_manager.test_connection()

        if result is True:
            QMessageBox.information(self, "Connexion réussie", f"Connecté à {server_ip}:{server_port}")
            self.create_file_interface()  # Créer l'interface fichier et redimensionner la fenêtre
        else:
            QMessageBox.critical(self, "Erreur de connexion", result)

    def create_file_interface(self):
        self.clear_layout()

        # Redimensionner la fenêtre pour l'interface de fichiers
        self.resize(1000, 800)  # Taille spécifique pour l'interface de fichier

        # Retour
        back_button = QPushButton("Retour")
        back_button.clicked.connect(self.create_connection_interface)
        self.layout.addWidget(back_button, 0, 0, 1, 2)

        # Type de fichier
        self.layout.addWidget(QLabel("Choix du type de fichier:"), 1, 0)
        self.file_type_selector = QComboBox()
        self.file_type_selector.addItems(["Python", "C", "Java"])
        self.layout.addWidget(self.file_type_selector, 1, 1)

        # Bouton pour charger un fichier
        load_button = QPushButton("Charger un fichier")
        load_button.clicked.connect(self.load_file)
        self.layout.addWidget(load_button, 2, 0, 1, 2)

        # Contenu du fichier
        self.file_content_edit = QTextEdit()
        self.layout.addWidget(self.file_content_edit, 3, 0, 1, 2)

        # Bouton pour envoyer le fichier
        send_button = QPushButton("Envoyer au serveur")
        send_button.clicked.connect(self.send_to_server)
        self.layout.addWidget(send_button, 4, 0, 1, 2)

        # Résultat
        self.layout.addWidget(QLabel("Résultat:"), 5, 0)
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.layout.addWidget(self.result_text, 6, 0, 1, 2)

    def load_file(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Charger un fichier", "", "Tous les fichiers (*)")
        if filepath:
            with open(filepath, "r") as file:
                content = file.read()
                self.file_content_edit.setPlainText(content)
            self.loaded_file_name = os.path.basename(filepath)

    def send_to_server(self):
        file_content = self.file_content_edit.toPlainText()
        file_type = self.file_type_selector.currentText()
        file_name = getattr(self, "loaded_file_name", "code")

        if file_content and file_type:
            self.thread = FileSenderThread(self.connection_manager, file_content, file_type, file_name)
            self.thread.result_signal.connect(self.display_result)
            self.thread.start()

    def display_result(self, result):
        self.result_text.setPlainText(result)

    def clear_layout(self):
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def light_theme_css(self):
        return """
            QWidget {
                background-color: #f9f9f9;
                color: #333333;
                font-family: 'Arial', sans-serif;
                font-size: 16px;
            }
            QLabel {
                font-size: 18px;
                font-weight: bold;
                margin-bottom: 10px;
            }
            QLineEdit, QTextEdit, QComboBox {
                background-color: #ffffff;
                color: #333333;
                border: 2px solid #cccccc;
                border-radius: 8px;
                padding: 8px;
                font-size: 16px;
            }
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
                border: 2px solid #4da6ff;
                outline: none;
            }
            QPushButton {
                background-color: #4da6ff;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0073e6;
            }
            QPushButton:pressed {
                background-color: #005bb5;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
            QTextEdit {
                font-family: 'Courier New', monospace;
                font-size: 14px;
            }
            QComboBox {
                font-size: 16px;
            }
        """


if __name__ == "__main__":
    app = QApplication(sys.argv)
    client = ClientApp()
    client.setStyleSheet(client.light_theme_css())  # Appliquer les styles
    client.show()
    sys.exit(app.exec_())
