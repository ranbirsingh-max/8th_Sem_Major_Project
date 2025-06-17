import sys
import requests
import base64
import json

from PIL import Image
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtWidgets import (
    QMainWindow, QFileDialog, QPushButton, QApplication,
    QLabel, QLineEdit, QMessageBox
)
from PyQt5.QtCore import Qt

from utils import generate_uuid


class NewCase(QMainWindow):
    def __init__(self, user: str):
        super().__init__()
        self.title = "Register New Case"
        self.name = None
        self.age = None
        self.mob = None
        self.father_name = None
        self.image = None
        self.encoded_image = None
        self.key_points = None
        self.user = user
        self._x_axis = 500
        self.initialize()

    def initialize(self):
        self.setFixedSize(800, 600)
        self.setWindowTitle(self.title)
        self.setStyleSheet("background-color: #121212; color: white;")

        font = QFont("Segoe UI", 10)

        self.upload_image_button = QPushButton("Upload Image", self)
        self.upload_image_button.resize(150, 50)
        self.upload_image_button.move(self._x_axis, 20)
        self.upload_image_button.setFont(font)
        self.upload_image_button.setStyleSheet("""
            QPushButton {
                background-color: #1e7e34;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #28a745;
            }
        """)
        self.upload_image_button.clicked.connect(self.openFileNameDialog)

        self.save_button = QPushButton("Save", self)
        self.save_button.resize(150, 50)
        self.save_button.move(self._x_axis, 350)
        self.save_button.setFont(font)
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #198754;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #28a745;
            }
        """)
        self.save_button.clicked.connect(self.save)

        self.get_name()
        self.get_age()
        self.get_fname()
        self.get_mob()
        self.show()

    def input_style(self):
        return "background-color: #1f1f1f; color: white; border: 1px solid #444; border-radius: 4px; padding: 4px;"

    def label_style(self):
        return "color: white; font-size: 13px;"

    def get_name(self):
        self.name_label = QLabel("Name:", self)
        self.name_label.move(self._x_axis, 100)
        self.name_label.setStyleSheet(self.label_style())

        self.name = QLineEdit(self)
        self.name.move(self._x_axis + 70, 100)
        self.name.setFixedWidth(200)
        self.name.setStyleSheet(self.input_style())

    def get_age(self):
        self.age_label = QLabel("Age:", self)
        self.age_label.move(self._x_axis, 150)
        self.age_label.setStyleSheet(self.label_style())

        self.age = QLineEdit(self)
        self.age.move(self._x_axis + 70, 150)
        self.age.setFixedWidth(200)
        self.age.setStyleSheet(self.input_style())

    def get_fname(self):
        self.fname_label = QLabel("Father's Name:", self)
        self.fname_label.move(self._x_axis, 200)
        self.fname_label.setStyleSheet(self.label_style())

        self.father_name = QLineEdit(self)
        self.father_name.move(self._x_axis + 70, 200)
        self.father_name.setFixedWidth(200)
        self.father_name.setStyleSheet(self.input_style())

    def get_mob(self):
        self.mob_label = QLabel("Mobile:", self)
        self.mob_label.move(self._x_axis, 250)
        self.mob_label.setStyleSheet(self.label_style())

        self.mob = QLineEdit(self)
        self.mob.move(self._x_axis + 70, 250)
        self.mob.setFixedWidth(200)
        self.mob.setStyleSheet(self.input_style())

    def get_facial_points(self, image_url) -> list:
        URL = "http://localhost:8002/image"
        f = [("image", open(image_url, "rb"))]
        try:
            result = requests.post(URL, files=f)
            if result.status_code == 200:
                return json.loads(result.text)["encoding"]
            else:
                QMessageBox.about(self, "Error", "Couldn't find face in Image")
                return None
        except Exception:
            QMessageBox.about(self, "Error", "Couldn't connect to face encoding API")
            return None

    def openFileNameDialog(self):
        options = QFileDialog.Options()
        self.fileName, _ = QFileDialog.getOpenFileName(
            self,
            "Select Image",
            "",
            "jpg file (*.jpg);;All Files (*)",
            options=options,
        )

        if self.fileName:
            self.key_points = self.get_facial_points(self.fileName)
            if self.key_points:
                label = QLabel(self)
                pixmap = QPixmap(self.fileName)
                pixmap = pixmap.scaled(320, 350, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                label.setPixmap(pixmap)
                label.resize(310, 350)
                label.move(50, 50)
                label.setStyleSheet("border: 1px solid #333;")
                label.show()

    def get_entries(self):
        entries = {}
        if (
            self.age.text() != ""
            and self.mob.text() != ""
            and self.name.text() != ""
            and self.father_name.text() != ""
        ):
            entries["age"] = self.age.text()
            entries["name"] = self.name.text()
            entries["father_name"] = self.father_name.text()
            entries["mobile"] = self.mob.text()
            return entries
        else:
            return None

    def save_to_db(self, entries):
        URL = "http://localhost:8000/new_case"
        headers = {"Content-Type": "application/json", "Accept": "application/json"}

        byte_content = open(self.fileName, "rb").read()
        base64_bytes = base64.b64encode(byte_content)
        base64_string = base64_bytes.decode("utf-8")

        entries["image"] = base64_string
        try:
            res = requests.post(URL, json.dumps(entries), headers=headers)
            if res.status_code == 200:
                QMessageBox.about(self, "Success", "Saved successfully")
            else:
                QMessageBox.about(self, "Error", "Something went wrong while saving")
        except Exception:
            QMessageBox.about(self, "Error", "Couldn't connect to database")

    def save(self):
        entries = self.get_entries()
        if entries:
            entries["face_encoding"] = self.key_points
            entries["submitted_by"] = self.user
            entries["case_id"] = generate_uuid()
            self.save_to_db(entries)
        else:
            QMessageBox.about(self, "Error", "Please fill all entries")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = NewCase("gagan")
    sys.exit(app.exec())
