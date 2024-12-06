import sys
import socket
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QStackedWidget, QWidget, QLabel, QLineEdit,
    QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QTextEdit, QFileDialog
)
from PyQt5.QtCore import QThread, pyqtSignal


# Thread pour surveiller l'utilisation CPU
class CPUUsageThread(QThread):
    cpu_signal = pyqtSignal(str)

    def __init__(self, server_ip, server_port):
        super().__init__()
        self.server_ip = server_ip
        self.server_port = server_port
        self.running = True

    def run(self):
        while self.running:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                    client_socket.connect((self.server_ip, self.server_port))
                    client_socket.sendall("CPU_USAGE".encode())
                    response = client_socket.recv(1024).decode()
                    self.cpu_signal.emit(response)
            except Exception as e:
                self.cpu_signal.emit(f"Erreur : {e}")
            self.msleep(1000)

    def stop(self):
        self.running = False


# Thread pour envoyer des fichiers
class FileSenderThread(QThread):
    result_signal = pyqtSignal(str)

    def __init__(self, server_ip, server_port, message):
        super().__init__()
        self.server_ip = server_ip
        self.server_port = server_port
        self.message = message

    def run(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                client_socket.connect((self.server_ip, self.server_port))
                client_socket.sendall(self.message.encode())
                response = client_socket.recv(4096).decode()
                self.result_signal.emit(response)
        except Exception as e:
            self.result_signal.emit(f"Erreur : {e}")


# Interface principale
class MainPage(QWidget):
    def __init__(self, server_ip, server_port):
        super().__init__()
        self.server_ip = server_ip
        self.server_port = server_port
        self.cpu_thread = None
        self.init_ui()
        self.set_stylesheet()

    def init_ui(self):
        layout = QVBoxLayout()

        # Sélection du type de fichier
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

        # Résultat du fichier
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        layout.addWidget(QLabel("Résultat :"))
        layout.addWidget(self.result_text)

        # Affichage du CPU
        self.cpu_text = QTextEdit()
        self.cpu_text.setReadOnly(True)
        layout.addWidget(QLabel("Utilisation du CPU :"))
        layout.addWidget(self.cpu_text)

        # Boutons pour surveiller le CPU
        cpu_button_layout = QHBoxLayout()
        self.start_cpu_button = QPushButton("Démarrer la surveillance CPU")
        self.start_cpu_button.clicked.connect(self.start_cpu_monitoring)
        cpu_button_layout.addWidget(self.start_cpu_button)

        self.stop_cpu_button = QPushButton("Arrêter la surveillance CPU")
        self.stop_cpu_button.clicked.connect(self.stop_cpu_monitoring)
        cpu_button_layout.addWidget(self.stop_cpu_button)
        layout.addLayout(cpu_button_layout)

        self.setLayout(layout)

    def set_stylesheet(self):
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
                background-color: #4CAF50;
                color: white;
                font-size: 14px;
                border-radius: 5px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)

    def load_file(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Charger un fichier", "", "Tous les fichiers (*)")
        if filepath:
            with open(filepath, "r") as file:
                content = file.read()
                self.file_content_edit.setPlainText(content)
            self.loaded_file_name = filepath.split("/")[-1]

    def send_to_server(self):
        file_content = self.file_content_edit.toPlainText()
        file_type = self.file_type_selector.currentText()
        file_name = getattr(self, "loaded_file_name", "code.py")

        if file_content:
            message = f"{file_type}\n{file_name}\n{file_content}"
            self.thread = FileSenderThread(self.server_ip, self.server_port, message)
            self.thread.result_signal.connect(self.display_result)
            self.thread.start()

    def start_cpu_monitoring(self):
        if self.cpu_thread is None or not self.cpu_thread.isRunning():
            self.cpu_thread = CPUUsageThread(self.server_ip, self.server_port)
            self.cpu_thread.cpu_signal.connect(self.display_cpu)
            self.cpu_thread.start()

    def stop_cpu_monitoring(self):
        if self.cpu_thread and self.cpu_thread.isRunning():
            self.cpu_thread.stop()
            self.cpu_thread = None

    def display_result(self, result):
        self.result_text.setPlainText(result)

    def display_cpu(self, cpu_usage):
        self.cpu_text.setPlainText(cpu_usage)


# Page de connexion
class ConnectionPage(QWidget):
    def __init__(self, switch_to_main):
        super().__init__()
        self.switch_to_main = switch_to_main
        self.init_ui()
        self.set_stylesheet()

    def init_ui(self):
        layout = QVBoxLayout()

        # Adresse IP
        layout.addWidget(QLabel("Adresse IP du serveur :"))
        self.ip_input = QLineEdit("127.0.0.1")
        layout.addWidget(self.ip_input)

        # Port
        layout.addWidget(QLabel("Port du serveur :"))
        self.port_input = QLineEdit("10000")
        layout.addWidget(self.port_input)

        # Bouton de connexion
        self.connect_button = QPushButton("Se connecter")
        self.connect_button.clicked.connect(self.connect)
        layout.addWidget(self.connect_button)

        self.setLayout(layout)

    def set_stylesheet(self):
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
        ip = self.ip_input.text()
        port = int(self.port_input.text())
        self.switch_to_main(ip, port)


# Application principale
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
        self.main_page = MainPage(ip, port)
        self.stack.addWidget(self.main_page)
        self.stack.setCurrentWidget(self.main_page)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    client_app = ClientApp()
    client_app.show()
    sys.exit(app.exec_())
