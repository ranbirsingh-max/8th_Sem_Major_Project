import sys
import json
import requests
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLineEdit,
    QLabel, QPushButton, QMessageBox, QFrame
)
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtCore import Qt
from app_window import AppWindow  # Your app logic


class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Secure Login")
        self.setFixedSize(400, 520)
        self.setWindowIcon(QIcon("profile.png"))  # Optional

        self.URL = "http://localhost:8000"
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(20)

        # Profile image
        image_label = QLabel()
        pixmap = QPixmap("profile.png").scaled(90, 90, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        image_label.setPixmap(pixmap)
        image_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(image_label)

        # Title
        title = QLabel("Welcome Back")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Frame around form
        form_frame = QFrame()
        form_layout = QVBoxLayout()
        form_layout.setSpacing(15)

        # Username input
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.username_input.setObjectName("inputField")
        form_layout.addWidget(self.username_input)

        # Password input
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Password")
        self.password_input.setObjectName("inputField")
        form_layout.addWidget(self.password_input)

        # Login button
        login_button = QPushButton("LOGIN")
        login_button.setObjectName("loginButton")
        login_button.clicked.connect(self.handle_login)
        form_layout.addWidget(login_button)

        form_frame.setLayout(form_layout)
        layout.addWidget(form_frame)

        central_widget.setLayout(layout)

    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Validation Error", "Please fill in all fields.")
            return

        try:
            response = requests.get(f"{self.URL}/login?username={username}&password={password}")
            data = json.loads(response.text)

            if data.get("status", False):
                self.app_window = AppWindow(user=username)
                self.app_window.show()  # Show the app window
                self.close()            # Close the login window
            else:
                QMessageBox.warning(self, "Login Failed", "Invalid credentials. Try again.")
        except requests.exceptions.ConnectionError:
            QMessageBox.critical(self, "Server Error", "Unable to connect to the server.")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    app.setStyleSheet("""
        QWidget {
            background-color: #1e1e2f;
            color: #ffffff;
            font-family: 'Segoe UI';
        }

        QLineEdit#inputField {
            background-color: #2c2f3c;
            border: 1px solid #3a3f52;
            border-radius: 6px;
            padding: 10px;
            color: #ffffff;
            font-size: 12pt;
        }

        QLineEdit#inputField:focus {
            border: 1px solid #6272a4;
        }

        QPushButton#loginButton {
            background-color: #6272a4;
            border: none;
            color: white;
            padding: 10px;
            font-weight: bold;
            font-size: 12pt;
            border-radius: 6px;
        }

        QPushButton#loginButton:hover {
            background-color: #7085b4;
        }

        QLabel {
            font-size: 13pt;
        }

        QFrame {
            background: transparent;
        }
    """)

    window = LoginWindow()
    window.show()  # Show the login window when the app starts

    sys.exit(app.exec())
