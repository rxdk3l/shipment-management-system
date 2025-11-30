# === Contribution by Leader – Raid Kellil – DevOps Project 2025 ===
# Application entry point

import sys
import logging
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

from .database import Database
from .login import LoginDialog
from .main_window import MainWindow


def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.FileHandler('shipment_manager.log'), logging.StreamHandler()]
    )

    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    db = Database()

    login = LoginDialog(db)
    if login.exec() == login.DialogCode.Accepted:
        window = MainWindow(db)
        window.showMaximized()
        sys.exit(app.exec())
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
