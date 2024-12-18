# Script client.py codé par G.Runser pour la SAE3.02
# Manuel d'utilisation disponible sur Github
# Code commenté - Plus d'informations sur le document de réponse

import sys
import socket
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QStackedWidget, QWidget, QLabel, QLineEdit,
    QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QTextEdit, QFileDialog
)
from PyQt5.QtCore import QThread, pyqtSignal


# Thread pour surveiller l'utilisation du CPU
class CPUUsageThread(QThread):
    # Signal envoyé à l'interface pour afficher l'utilisation du CPU
    cpu_signal = pyqtSignal(str)

    def __init__(self, server_ip, server_port):
        super().__init__()
        self.server_ip = server_ip  # Adresse IP du serveur
        self.server_port = server_port  # Port du serveur
        self.running = True  # Indicateur pour contrôler l'exécution du thread

    def run(self):
        while self.running:
            try:
                # Connexion au serveur et demande de l'utilisation du CPU
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                    client_socket.connect((self.server_ip, self.server_port))
                    client_socket.sendall("CPU_USAGE".encode())
                    response = client_socket.recv(1024).decode()
                    # Envoi de la réponse au thread principal
                    self.cpu_signal.emit(response)
            except Exception as e:
                # En cas d'erreur, émettre l'exception
                self.cpu_signal.emit(f"Erreur : {e}")
            self.msleep(1000)  # Délai de 1 seconde entre chaque demande

    def stop(self):
        self.running = False  # Arrêter le thread


# Thread pour envoyer un fichier au serveur
class FileSenderThread(QThread):
    # Signal pour afficher le résultat de l'envoi
    result_signal = pyqtSignal(str)

    def __init__(self, server_ip, server_port, message):
        super().__init__()
        self.server_ip = server_ip  # Adresse IP du serveur
        self.server_port = server_port  # Port du serveur
        self.message = message  # Message à envoyer (contenant le fichier)

    def run(self):
        try:
            # Connexion au serveur et envoi du message
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                client_socket.connect((self.server_ip, self.server_port))
                client_socket.sendall(self.message.encode())
                # Réception de la réponse du serveur
                response = client_socket.recv(4096).decode()
                self.result_signal.emit(response)  # Affichage du résultat
        except Exception as e:
            # En cas d'erreur, émettre l'exception
            self.result_signal.emit(f"Erreur : {e}")

    def join(self):
        super().wait()  # Attendre la fin du thread


# Page principale de l'application client
class MainPage(QWidget):
    def __init__(self, server_ip, server_port):
        super().__init__()
        self.server_ip = server_ip  # Adresse IP du serveur
        self.server_port = server_port  # Port du serveur
        self.cpu_thread = None  # Thread pour la surveillance du CPU
        self.init_ui()  # Initialisation de l'interface utilisateur
        self.set_stylesheet()  # Application du style CSS

    def init_ui(self):
        layout = QVBoxLayout()

        # Sélection du type de fichier (Python, C, Java)
        file_type_layout = QHBoxLayout()
        file_type_layout.addWidget(QLabel("Type de fichier :"))
        self.file_type_selector = QComboBox()
        self.file_type_selector.addItems(["Python", "C", "Java"])
        file_type_layout.addWidget(self.file_type_selector)
        layout.addLayout(file_type_layout)

        # Zone de texte pour le contenu du fichier
        self.file_content_edit = QTextEdit()
        self.file_content_edit.setPlaceholderText("Contenu du fichier...")
        layout.addWidget(self.file_content_edit)

        # Boutons pour charger et envoyer des fichiers
        button_layout = QHBoxLayout()
        self.load_button = QPushButton("Charger un fichier")
        self.load_button.clicked.connect(self.load_file)
        button_layout.addWidget(self.load_button)

        self.send_button = QPushButton("Envoyer au serveur")
        self.send_button.clicked.connect(self.send_to_server)
        button_layout.addWidget(self.send_button)
        layout.addLayout(button_layout)

        # Affichage du résultat de l'exécution du fichier
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        layout.addWidget(QLabel("Résultat :"))
        layout.addWidget(self.result_text)

        # Affichage de l'utilisation du CPU
        self.cpu_text = QTextEdit()
        self.cpu_text.setReadOnly(True)
        layout.addWidget(QLabel("Utilisation du CPU :"))
        layout.addWidget(self.cpu_text)

        # Bouton pour démarrer/arrêter la surveillance du CPU
        self.cpu_on_off_button = QPushButton("Démarrer la surveillance CPU")
        self.cpu_on_off_button.clicked.connect(self.toggle_cpu_monitoring)
        layout.addWidget(self.cpu_on_off_button)

        self.setLayout(layout)

    def set_stylesheet(self):
        # Style CSS pour l'interface
        self.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
            }
            QTextEdit, QComboBox {
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 5px;
                font-family: Consolas, monospace;
                background-color: #f9f9f9;
            }
            QPushButton {
                background-color: #FF8400;
                color: white;
                font-size: 14px;
                border-radius: 5px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #ba4a00;
            }
            QPushButton:disabled {
                background-color: #e0e0e0; /* Couleur grisée */
                color: #a0a0a0; /* Texte grisé */
                border: 1px solid #d0d0d0; /* Bordure grisée */
            }
        """)

    def load_file(self):
        # Ouvrir un fichier et charger son contenu dans la zone de texte
        filepath, _ = QFileDialog.getOpenFileName(self, "Charger un fichier", "", "Tous les fichiers (*)")
        if filepath:
            with open(filepath, "r") as file:
                content = file.read()
                self.file_content_edit.setPlainText(content)
            self.loaded_file_name = filepath.split("/")[-1]

    def send_to_server(self):
        # Envoyer le fichier au serveur
        file_content = self.file_content_edit.toPlainText()
        file_type = self.file_type_selector.currentText()
        file_name = getattr(self, "loaded_file_name", "code.py")

        if file_content:
            self.result_text.clear()  # Effacer le texte précédent
            self.send_button.setDisabled(True)  # Désactiver le bouton pendant l'envoi

            message = f"{file_type}\n{file_name}\n{file_content}"
            self.thread = FileSenderThread(self.server_ip, self.server_port, message)
            self.thread.result_signal.connect(self.display_result)  # Afficher le résultat
            self.thread.finished.connect(lambda: self.send_button.setDisabled(False))  # Réactiver le bouton
            self.thread.start()

    def toggle_cpu_monitoring(self):
        # Démarrer ou arrêter la surveillance du CPU
        if self.cpu_thread and self.cpu_thread.isRunning():
            self.stop_cpu_monitoring()
        else:
            self.start_cpu_monitoring()

    def start_cpu_monitoring(self):
        # Démarre la surveillance du CPU si ce n'est pas déjà fait
        if not self.cpu_thread or not self.cpu_thread.isRunning():
            self.cpu_on_off_button.setText("Arrêter la surveillance CPU")
            self.cpu_thread = CPUUsageThread(self.server_ip, self.server_port)
            self.cpu_thread.cpu_signal.connect(self.display_cpu)  # Afficher l'utilisation du CPU
            self.cpu_thread.start()

    def stop_cpu_monitoring(self):
        # Arrête la surveillance du CPU
        if self.cpu_thread and self.cpu_thread.isRunning():
            self.cpu_thread.stop()
            self.cpu_thread = None
            self.cpu_on_off_button.setText("Démarrer la surveillance CPU")

    def display_result(self, result):
        # Afficher le résultat de l'exécution du fichier
        self.result_text.setPlainText(result)

    def display_cpu(self, cpu_usage):
        # Afficher l'utilisation du CPU
        self.cpu_text.setPlainText(cpu_usage)


# Page de connexion pour entrer l'IP et le port du serveur
class ConnectionPage(QWidget):
    def __init__(self, switch_to_main):
        super().__init__()
        self.switch_to_main = switch_to_main  # Fonction pour changer de page
        self.init_ui()  # Initialisation de l'interface utilisateur
        self.set_stylesheet()  # Application du style CSS

    def init_ui(self):
        layout = QVBoxLayout()

        # Adresse IP
        layout.addWidget(QLabel("Adresse IP du serveur :"))
        self.ip_input = QLineEdit("127.0.0.1")  # Valeur par défaut
        layout.addWidget(self.ip_input)

        # Port
        layout.addWidget(QLabel("Port du serveur :"))
        self.port_input = QLineEdit("10000")  # Valeur par défaut
        layout.addWidget(self.port_input)

        # Bouton de connexion
        self.connect_button = QPushButton("Se connecter")
        self.connect_button.clicked.connect(self.connect)
        layout.addWidget(self.connect_button)

        self.setLayout(layout)

    def set_stylesheet(self):
        # Style CSS pour la page de connexion
        self.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
            }
            QLineEdit {
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 5px;
                font-size: 12px;
            }
            QPushButton {
                background-color: #007BFF;
                color: white;
                font-size: 14px;
                border-radius: 5px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)

    def connect(self):
        # Connexion au serveur avec l'IP et le port fournis
        ip = self.ip_input.text()
        port = int(self.port_input.text())
        self.switch_to_main(ip, port)


# Classe principale de l'application client
class ClientApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Client Serveur")

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Pages
        self.connection_page = ConnectionPage(self.switch_to_main)
        self.stack.addWidget(self.connection_page)

    def switch_to_main(self, ip, port):
        # Passer à la page principale après la connexion réussie
        self.main_page = MainPage(ip, port)
        self.stack.addWidget(self.main_page)
        self.stack.setCurrentWidget(self.main_page)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    client_app = ClientApp()
    client_app.show()
    sys.exit(app.exec_())
