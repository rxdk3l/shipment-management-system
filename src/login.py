# === Contribution by Leader – Raid Kellil – DevOps Project 2025 ===
# Full login system with secure password hashing

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QLabel,
    QDialogButtonBox, QMessageBox, QFont
)
from PyQt6.QtCore import Qt
import hashlib
import logging

from .database import Database


class LoginDialog(QDialog):
    def __init__(self, db: Database):
        super().__init__()
        self.db = db
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Login - Shipment Management System")
        self.setFixedSize(400, 300)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)

        layout = QVBoxLayout()

        title = QLabel("Shipment Management System")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        layout.addSpacing(20)

        username_layout = QFormLayout()
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter username")
        username_layout.addRow("Username:", self.username_input)
        layout.addLayout(username_layout)

        password_layout = QFormLayout()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Enter password")
        password_layout.addRow("Password:", self.password_input)
        layout.addLayout(password_layout)

        layout.addSpacing(20)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)
        self.username_input.setFocus()

    def accept(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()

        if not username or not password:
            QMessageBox.warning(self, "Error", "Please enter both username and password")
            return

        password_hash = hashlib.sha256(password.encode()).hexdigest()
        results = self.db.execute_query(
            'SELECT id FROM users WHERE username = ? AND password_hash = ?',
            (username, password_hash)
        )

        if results:
            super().accept()
        else:
            QMessageBox.warning(self, "Error", "Invalid username or password")
            logging.warning(f"Failed login attempt for username: {username}")
