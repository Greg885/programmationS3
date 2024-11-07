import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox


class SimpleApp(QWidget):
    def __init__(self):
        super().__init__()

        # Configuration de la fenêtre principale
        self.setWindowTitle("Une première fenêtre")
        self.setGeometry(100, 100, 300, 150)

        # Création des widgets
        self.label = QLabel("Saisir votre nom", self)
        self.name_input = QLineEdit(self)

        self.ok_button = QPushButton("Ok", self)
        self.ok_button.clicked.connect(self.greet_user)

        self.quit_button = QPushButton("Quitter", self)
        self.quit_button.clicked.connect(self.close)

        # Disposition des widgets
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.name_input)
        layout.addWidget(self.ok_button)
        layout.addWidget(self.quit_button)

        self.setLayout(layout)

    def greet_user(self):
        name = self.name_input.text()
        if name:
            QMessageBox.information(self, "Message", f"Bonjour {name} !")
        else:
            QMessageBox.warning(self, "Attention", "Veuillez entrer un nom.")


# Exécution de l'applicatio
app = QApplication(sys.argv)
window = SimpleApp()
window.show()
sys.exit(app.exec_())
