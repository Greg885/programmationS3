import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QComboBox, QLabel, QLineEdit, QVBoxLayout, QPushButton, QWidget

class MyWindow(QMainWindow):
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

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Apply CSS styles
        self.apply_styles()

    def apply_styles(self):
        # Define CSS for each widget
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
            temp = float(self.name_input1.text())  # Get temperature input from user
            conversion_type = self.combobox.currentText()  # Get selected conversion

            if conversion_type == "C -> K":
                result = temp + 273.15
            else:
                result = temp - 273.15

            self.result_label.setText(f"Résultat: {result:.2f}")
        except ValueError:
            self.result_label.setText("Entrez un nombre")

app = QApplication(sys.argv)
window = MyWindow()
window.show()
sys.exit(app.exec())
