# === Contribution by Member 3 – radjab beddiar – DevOps Project 2025 ===
# Farmers list, transfers, returns

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QLabel, QDialog, QFormLayout, QComboBox,
    QDoubleSpinBox, QTextEdit, QDialogButtonBox, QMessageBox
)
from PyQt6.QtGui import QFont
from decimal import Decimal

from .database import Database


class FarmersWidget(QWidget):
    def __init__(self, db: Database):
        super().__init__()
        self.db = db
        self.init_ui()
        self.load_farmers()

    def init_ui(self):
        layout = QVBoxLayout()

        header = QHBoxLayout()
        header.addWidget(QLabel("<h2>Farmers</h2>"))
        header.addStretch()

        QPushButton("Add Farmer", clicked=self.add_farmer).setParent(self)
        header.addWidget(QPushButton("Add Farmer", clicked=self.add_farmer))
        header.addWidget(QPushButton("Transfer Products", clicked=self.transfer_products))
        header.addWidget(QPushButton("Record Return", clicked=self.record_return))

        layout.addLayout(header)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Name", "Date Added", "Total Bought (DA)"])
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)

        self.setLayout(layout)

    def load_farmers(self):
        query = '''
            SELECT f.id, f.name, f.created_at,
                   COALESCE(SUM(fp.total_paid), 0) as total_bought
            FROM farmers f
            LEFT JOIN farmer_purchases fp ON f.id = fp.farmer_id
            GROUP BY f.id
            ORDER BY f.name
        '''
        farmers = self.db.execute_query(query)
        self.table.setRowCount(len(farmers))
        for row, f in enumerate(farmers):
            self.table.setItem(row, 0, QTableWidgetItem(f['name']))
            self.table.setItem(row, 1, QTableWidgetItem(f['created_at'][:10].replace('-', '/')))
            total = Decimal(str(f['total_bought'])).quantize(Decimal('0.01'))
            self.table.setItem(row, 2, QTableWidgetItem(f"{total:,.2f} DA"))

    def add_farmer(self):
        from PyQt6.QtWidgets import QInputDialog
        name, ok = QInputDialog.getText(self, "Add Farmer", "Farmer name:")
        if ok and name.strip():
            try:
                self.db.execute_update('INSERT INTO farmers (name) VALUES (?)', (name.strip(),))
                self.load_farmers()
            except:
                QMessageBox.warning(self, "Error", "Name already exists")

    def transfer_products(self):
        TransferDialog(self.db).exec()
        self.load_farmers()

    def record_return(self):
        ReturnDialog(self.db).exec()
        self.load_farmers()


class TransferDialog(QDialog):
    def __init__(self, db: Database):
        super().__init__()
        self.db = db
        self.setWindowTitle("Transfer Products")
        self.resize(500, 400)
        layout = QVBoxLayout()

        form = QFormLayout()
        self.from_combo = QComboBox()
        self.to_combo = QComboBox()
        self.product_combo = QComboBox()
        self.qty_spin = QDoubleSpinBox()
        self.qty_spin.setRange(0.01, 999999)
        self.note = QTextEdit()

        for combo in [self.from_combo, self.to_combo]:
            for f in db.execute_query('SELECT id, name FROM farmers ORDER BY name'):
                combo.addItem(f['name'], f['id'])
        for p in db.execute_query('SELECT id, name FROM products ORDER BY name'):
            self.product_combo.addItem(p['name'], p['id'])

        form.addRow("From Farmer:", self.from_combo)
        form.addRow("To Farmer:", self.to_combo)
        form.addRow("Product:", self.product_combo)
        form.addRow("Quantity:", self.qty_spin)
        form.addRow("Note:", self.note)
        layout.addLayout(form)

        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(self.transfer)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)
        self.setLayout(layout)

    def transfer(self):
        if self.from_combo.currentData() == self.to_combo.currentData():
            QMessageBox.warning(self, "Error", "Cannot transfer to same farmer")
            return
        self.db.execute_update('''
            INSERT INTO transfers 
            (from_farmer_id, to_farmer_id, product_id, quantity, note)
            VALUES (?, ?, ?, ?, ?)
        ''', (self.from_combo.currentData(), self.to_combo.currentData(),
              self.product_combo.currentData(), self.qty_spin.value(),
              self.note.toPlainText()))
        QMessageBox.information(self, "Success", "Transfer recorded")
        self.accept()


class ReturnDialog(QDialog):
    def __init__(self, db: Database):
        super().__init__()
        self.db = db
        self.setWindowTitle("Record Return")
        self.resize(500, 400)
        layout = QVBoxLayout()

        form = QFormLayout()
        self.farmer_combo = QComboBox()
        self.product_combo = QComboBox()
        self.qty_spin = QDoubleSpinBox()
        self.qty_spin.setRange(0.01, 999999)
        self.refund_spin = QDoubleSpinBox()
        self.refund_spin.setRange(0, 999999)
        self.refund_spin.setPrefix("DA ")
        self.note = QTextEdit()

        for f in db.execute_query('SELECT id, name FROM farmers ORDER BY name'):
            self.farmer_combo.addItem(f['name'], f['id'])
        for p in db.execute_query('SELECT id, name FROM products ORDER BY name'):
            self.product_combo.addItem(p['name'], p['id'])

        form.addRow("Farmer:", self.farmer_combo)
        form.addRow("Product:", self.product_combo)
        form.addRow("Quantity:", self.qty_spin)
        form.addRow("Refund Amount:", self.refund_spin)
        form.addRow("Note:", self.note)
        layout.addLayout(form)

        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(self.record)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)
        self.setLayout(layout)

    def record(self):
        self.db.execute_update('''
            INSERT INTO returns 
            (farmer_id, product_id, quantity, refund_amount, note)
            VALUES (?, ?, ?, ?, ?)
        ''', (self.farmer_combo.currentData(), self.product_combo.currentData(),
              self.qty_spin.value(), self.refund_spin.value(), self.note.toPlainText()))
        QMessageBox.information(self, "Success", "Return recorded")
        self.accept()
