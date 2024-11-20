import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QVBoxLayout, QPushButton, QComboBox, QMessageBox
from PyQt6.QtGui import QAction  # Importer QAction depuis QtGui
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
            QMessageBox.information(self, "Message d'information", f"Bonjour {name} {surname} !")
        else:
            QMessageBox.warning(self, "Attention", "Veuillez entrer l'information manquante.")


class MyWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Ex2 - Météo")
        self.setGeometry(200, 200, 300, 200)

        # Create widgets
        self.label1 = QLabel("Saisir la température:", self)
        self.name_input1 = QLineEdit(self)
        self.result_label = QLabel("", self)

        self.ok_button = QPushButton("Convertir", self)
        self.ok_button.clicked.connect(self.convert_temperature)

        # ComboBox for selecting conversion type
        self.combobox = QComboBox(self)
        self.combobox.addItem("C -> K")
        self.combobox.addItem("K -> C")

        # Layout setup
        layout = QVBoxLayout()
        layout.addWidget(self.label1)
        layout.addWidget(self.name_input1)
        layout.addWidget(self.combobox)
        layout.addWidget(self.ok_button)
        layout.addWidget(self.result_label)

        self.setLayout(layout)

        # Apply CSS styles
        self.apply_styles()

    def apply_styles(self):
        self.setStyleSheet("background-color: #f0f0f0;")
        self.label1.setStyleSheet("font-size: 14px; color: #333333;")
        self.name_input1.setStyleSheet("""
            padding: 5px;
            font-size: 14px;
            border: 1px solid #cccccc;
            border-radius: 5px;
        """)
        self.result_label.setStyleSheet("font-size: 16px; color: #0066cc; font-weight: bold;")
        self.ok_button.setStyleSheet("""
            background-color: #4CAF50;
            color: white;
            font-size: 14px;
            padding: 5px;
            border-radius: 5px;
        """)
        self.combobox.setStyleSheet("""
            font-size: 14px;
            padding: 5px;
            border: 1px solid #cccccc;
            border-radius: 5px;
        """)

    def convert_temperature(self):
        try:
            temp = float(self.name_input1.text())
            conversion_type = self.combobox.currentText()

            if conversion_type == "C -> K":
                result = temp + 273.15
            else:
                result = temp - 273.15

            self.result_label.setText(f"Résultat: {result:.2f}")
        except ValueError:
            self.result_label.setText("Entrez un nombre")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Application avec Menu")
        self.setGeometry(100, 100, 400, 300)

        # Initialiser les fenêtres secondaires
        self.ex1_window = EX1()
        self.my_window = MyWindow()

        # Création du menu
        menu_bar = self.menuBar()
        window_menu = menu_bar.addMenu("Choisir la fenêtre")

        # Ajouter les actions de menu pour afficher les fenêtres
        ex1_action = QAction("Fenêtre EX1", self)
        ex1_action.triggered.connect(self.show_ex1_window)
        window_menu.addAction(ex1_action)

        my_window_action = QAction("Fenêtre MyWindow", self)
        my_window_action.triggered.connect(self.show_my_window)
        window_menu.addAction(my_window_action)

    def show_ex1_window(self):
        self.setCentralWidget(self.ex1_window)

    def show_my_window(self):
        self.setCentralWidget(self.my_window)


# Exécution de l'application
app = QApplication(sys.argv)
main_window = MainWindow()
main_window.show()
sys.exit(app.exec())
