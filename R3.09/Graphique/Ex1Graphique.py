import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox


class EX1(QWidget):
    def __init__(self):
        super().__init__()

        # Configuration de la fenêtre principale
        self.setWindowTitle("Une première fenêtre")
        self.setGeometry(100, 100, 300, 150)

        # Création des widgets
        self.label1 = QLabel("Saisir votre Nom", self)
        self.name_input1 = QLineEdit(self)

        self.label2 = QLabel("Saisir votre Prénom", self)
        self.name_input2 = QLineEdit(self)

        self.ok_button = QPushButton("Ok", self)
        self.ok_button.clicked.connect(self.greet_user)

        self.quit_button = QPushButton("Quitter", self)
        self.quit_button.clicked.connect(self.close)

        # Disposition des widgets
        layout = QVBoxLayout()
        layout.addWidget(self.label1)
        layout.addWidget(self.name_input1)
        layout.addWidget(self.label2)
        layout.addWidget(self.name_input2)
        layout.addWidget(self.ok_button)
        layout.addWidget(self.quit_button)

        self.setLayout(layout)

    def greet_user(self):
        name = self.name_input1.text()
        surname = self.name_input2.text()
        if name and surname:
            QMessageBox.information(self, f"Message d'information", f"Bonjour {name} {surname} !")
        else:
            QMessageBox.warning(self, "Attention", "Veuillez entrer l'information manquante.")


# Exécution de l'application
app = QApplication(sys.argv)
window = EX1()
window.show()
sys.exit(app.exec_())
