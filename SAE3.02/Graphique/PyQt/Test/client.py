import sys
import socket
from PyQt5.QtWidgets import (QApplication, QWidget, QGridLayout, QPushButton, QLabel, QLineEdit, QTextEdit, QFileDialog, QComboBox)
from PyQt5.QtCore import QThread, pyqtSignal, Qt
import os


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
                self.cpu_signal.emit(f"Erreur lors de la récupération du CPU : {e}")
            self.msleep(1000)

    def stop(self):
        self.running = False


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
            self.result_signal.emit(f"Erreur lors de l'envoi : {e}")


class ClientApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Client avec gestion CPU en direct et fichiers")
        self.cpu_thread = None
        self.init_ui()
        self.set_stylesheet()

    def init_ui(self):
        self.layout = QGridLayout()
        self.setLayout(self.layout)

        # Adresse IP du serveur
        self.layout.addWidget(QLabel("Adresse IP du serveur :"), 0, 0)
        self.master_ip_input = QLineEdit("127.0.0.1")
        self.layout.addWidget(self.master_ip_input, 0, 1)

        # Port du serveur
        self.layout.addWidget(QLabel("Port du serveur :"), 1, 0)
        self.master_port_input = QLineEdit("10000")
        self.layout.addWidget(self.master_port_input, 1, 1)

        # Type de fichier
        self.layout.addWidget(QLabel("Type de fichier :"), 2, 0)
        self.file_type_selector = QComboBox()
        self.file_type_selector.addItems(["Python", "C", "Java"])
        self.layout.addWidget(self.file_type_selector, 2, 1)

        # Bouton pour charger un fichier
        self.load_button = QPushButton("Charger un fichier")
        self.load_button.clicked.connect(self.load_file)
        self.layout.addWidget(self.load_button, 3, 0, 1, 2)

        # Contenu du fichier
        self.layout.addWidget(QLabel("Contenu du fichier :"), 4, 0)
        self.file_content_edit = QTextEdit()
        self.layout.addWidget(self.file_content_edit, 5, 0, 1, 2)

        # Bouton pour envoyer un fichier
        self.send_button = QPushButton("Envoyer au serveur")
        self.send_button.clicked.connect(self.send_to_master)
        self.layout.addWidget(self.send_button, 6, 0, 1, 2)

        # Résultat du fichier traité par le serveur
        self.layout.addWidget(QLabel("Résultat du fichier :"), 7, 0)
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.layout.addWidget(self.result_text, 8, 0, 1, 2)

        # Résultat de l'utilisation du CPU (direct)
        self.layout.addWidget(QLabel("Utilisation du CPU : (si >70% lancement d'un second serveur)"), 9, 0)
        self.cpu_text = QTextEdit()
        self.cpu_text.setReadOnly(True)
        self.layout.addWidget(self.cpu_text, 10, 0, 1, 2)

        # Bouton pour démarrer la surveillance CPU
        self.start_cpu_button = QPushButton("Démarrer la surveillance CPU")
        self.start_cpu_button.clicked.connect(self.start_cpu_monitoring)
        self.layout.addWidget(self.start_cpu_button, 11, 0, 1, 1)

        # Bouton pour arrêter la surveillance CPU
        self.stop_cpu_button = QPushButton("Arrêter la surveillance CPU")
        self.stop_cpu_button.clicked.connect(self.stop_cpu_monitoring)
        self.layout.addWidget(self.stop_cpu_button, 11, 1, 1, 1)

    def set_stylesheet(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
                color: #333;
                font-family: Arial, sans-serif;
            }
            QLabel {
                font-size: 14px;
                font-weight: bold;
            }
            QLineEdit, QTextEdit, QComboBox {
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 5px;
                font-size: 12px;
                background-color: #fff;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-size: 14px;
                cursor: pointer;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QTextEdit {
                font-family: Consolas, monospace;
                font-size: 12px;
                color: #333;
            }
        """)

    def load_file(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Charger un fichier", "", "Tous les fichiers (*)")
        if filepath:
            with open(filepath, "r") as file:
                content = file.read()
                self.file_content_edit.setPlainText(content)
            self.loaded_file_name = os.path.basename(filepath)

    def send_to_master(self):
        file_content = self.file_content_edit.toPlainText()
        file_type = self.file_type_selector.currentText()
        file_name = getattr(self, "loaded_file_name", "code.py")

        if file_content:
            message = f"{file_type}\n{file_name}\n{file_content}"
            self.thread = FileSenderThread(self.master_ip_input.text(), int(self.master_port_input.text()), message)
            self.thread.result_signal.connect(self.display_file_result)
            self.thread.start()

    def start_cpu_monitoring(self):
        if self.cpu_thread is None or not self.cpu_thread.isRunning():
            self.cpu_thread = CPUUsageThread(self.master_ip_input.text(), int(self.master_port_input.text()))
            self.cpu_thread.cpu_signal.connect(self.display_cpu_result)
            self.cpu_thread.start()

    def stop_cpu_monitoring(self):
        if self.cpu_thread and self.cpu_thread.isRunning():
            self.cpu_thread.stop()
            self.cpu_thread = None

    def display_file_result(self, result):
        self.result_text.setPlainText(result)

    def display_cpu_result(self, result):
        self.cpu_text.setPlainText(result)

    def closeEvent(self, event):
        self.stop_cpu_monitoring()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    client = ClientApp()
    client.show()
    sys.exit(app.exec_())
