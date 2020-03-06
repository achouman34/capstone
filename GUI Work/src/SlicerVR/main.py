from PyQt5 import uic
from PyQt5.QtWidgets import QApplication

# Load UI design exported from QT Designer program.
Form, Window = uic.loadUiType("Capstone.ui")

app = QApplication([])
window = Window()
form = Form()
form.setupUi(window)

def on_button_clicked():
    alert = QMessageBox()
    alert.setText('You clicked the button!')
    alert.exec_()

pushButton.clicked.connect(on_button_clicked)

window.show()
app.exec_()
