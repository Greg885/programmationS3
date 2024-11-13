import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QComboBox, QLabel, QLineEdit, QVBoxLayout, QPushButton, QWidget

class Meteo(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Exo2 Météo")
        self.setGeometry(200, 200, 300, 200)

        # Create widgets
        self.label1 = QLabel("Saisir la température:", self)
        self.name_input1 = QLineEdit(self)
        self.result_label = QLabel("", self)

        self.ok_button = QPushButton("Convert", self)
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

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def convert_temperature(self):
        try:
            temp = float(self.name_input1.text())
            conversion_type = self.combobox.currentText()

            if conversion_type == "C -> K":
                result = temp + 273.15
            else:
                result = temp - 273.15

            self.result_label.setText(f"Resultat convertir en {conversion_type} : {result}")
        except ValueError:
            self.result_label.setText("Entrez un nombre valide")

app = QApplication(sys.argv)
window = Meteo()
window.show()
sys.exit(app.exec())
