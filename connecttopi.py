from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QMessageBox
)
from PyQt5.QtCore import pyqtSignal
import paramiko

RASPBERRY_PI_IP = "10.20.1.1"  # Replace with your Pi's IP

class PiLoginWidget(QWidget):
    # Signal that emits an SSH client object on successful login
    login_successful = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Raspberry Pi Login")

        # Create widgets
        self.username_label = QLabel("Username:")
        self.username_input = QLineEdit()

        self.password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)

        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.connect_to_pi)

        # Layout setup
        layout = QVBoxLayout()
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.connect_button)
        self.setLayout(layout)

    def connect_to_pi(self):
        username = self.username_input.text()
        password = self.password_input.text()

        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(RASPBERRY_PI_IP, username=username, password=password)
            QMessageBox.information(self, "Success", "Successfully connected to Raspberry Pi!")

            self.login_successful.emit(ssh)  # ✅ Emit the signal
            self.close()

        except Exception as e:
            QMessageBox.critical(self, "Connection Failed", str(e))
