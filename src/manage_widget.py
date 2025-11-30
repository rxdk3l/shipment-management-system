# === Contribution by Member 2 – [Member 2 Name] – DevOps Project 2025 ===
# Direct warehouse sales + current stock overview

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QFormLayout, QTableWidget,
    QTableWidgetItem, QComboBox, QDoubleSpinBox, QPushButton,
    QHBoxLayout, QLabel, QMessageBox
)
from PyQt6.QtGui import QFont
from decimal import Decimal

from .database import Database


class ManageWidget(QWidget):
    def __init__(self, db: Database):
        super().__init__()
        self.db = db
        self.init_ui()
        self.load_stock()
        self.load_combos()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel("<h2>Stock Management</h2>"))

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([
            "Product", "Total Bought", "Total Sold", "Current Stock"
        ])
        layout.addWidget(self.table)

        # Direct sale box
        sale_group = QGroupBox("Direct Warehouse Sale")
        sale_layout = QFormLayout()

        self.farmer_combo = QComboBox()
        self.product_combo = QComboBox()
        self.quantity_spin = QDoubleSpinBox()
        self.quantity_spin.setRange(0.01, 100000)
        self.price_spin = QDoubleSpinBox()
        self.price_spin.setRange(0.01, 100000)
        self.price_spin.setPrefix("DA ")

        sale_layout.addRow("Farmer:", self.farmer_combo)
        sale_layout.addRow("Product:", self.product_combo)
        sale_layout.addRow("Quantity:", self.quantity_spin)
        sale_layout.addRow("Unit Price:", self.price_spin)

        sell_btn = QPushButton("Sell")
        sell_btn.clicked.connect(self.direct_sell)
        sale_layout.addRow(sell_btn)

        sale_group.setLayout(sale_layout)
        layout.addWidget(sale_group)

        self.setLayout(layout)

    def load_combos(self):
        farmers = self.db.execute_query('SELECT id, name FROM farmers ORDER BY name')
        self.farmer_combo.clear()
        for f in farmers:
            self.farmer_combo.addItem(f['name'], f['id'])

        products = self.db.execute_query('SELECT id, name FROM products ORDER BY name')
        self.product_combo.clear()
        for p in products:
            self.product_combo.addItem(p['name'], p['id'])

    def load_stock(self):
        query = '''
            SELECT p.name,
                   COALESCE(SUM(sp.quantity), 0) as total_bought,
                   COALESCE(SUM(fp.quantity), 0) as total_sold,
                   COALESCE(SUM(sp.quantity), 0) - 
                   COALESCE(SUM(fp.quantity), 0) - 
                   COALESCE(SUM(r.quantity), 0) as current_stock
            FROM products p
            LEFT JOIN shipment_products sp ON p.id = sp.product_id
            LEFT JOIN farmer_purchases fp ON p.id = fp.product_id
            LEFT JOIN returns r ON p.id = r.product_id
            GROUP BY p.id
            ORDER BY p.name
        '''
        data = self.db.execute_query(query)
        self.table.setRowCount(len(data))
        for row, item in enumerate(data):
            self.table.setItem(row, 0, QTableWidgetItem(item['name']))
            self.table.setItem(row, 1, QTableWidgetItem(f"{Decimal(str(item['total_bought'])):,.2f}"))
            self.table.setItem(row, 2, QTableWidgetItem(f"{Decimal(str(item['total_sold'])):,.2f}"))
            self.table.setItem(row, 3, QTableWidgetItem(f"{Decimal(str(item['current_stock'])):,.2f}"))

    def direct_sell(self):
        farmer_id = self.farmer_combo.currentData()
        product_id = self.product_combo.currentData()
        quantity = self.quantity_spin.value()
        unit_price = self.price_spin.value()
        total = quantity * unit_price

        if quantity <= 0 or unit_price <= 0:
            QMessageBox.warning(self, "Error", "Invalid quantity or price")
            return

        self.db.execute_update('''
            INSERT INTO farmer_purchases 
            (farmer_id, product_id, quantity, unit_price, total_paid)
            VALUES (?, ?, ?, ?, ?)
        ''', (farmer_id, product_id, quantity, unit_price, total))

        QMessageBox.information(self, "Success", "Direct sale recorded")
        self.load_stock()
        self.quantity_spin.setValue(0.01)
        self.price_spin.setValue(0.01)
