# === Contribution by Member 2 –maou houssem eddin – DevOps Project 2025 ===
# Full Products management + statistics

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QLabel, QMessageBox, QInputDialog
)
from PyQt6.QtGui import QFont
from decimal import Decimal

from .database import Database


class ProductsWidget(QWidget):
    def __init__(self, db: Database):
        super().__init__()
        self.db = db
        self.init_ui()
        self.load_products()

    def init_ui(self):
        layout = QVBoxLayout()

        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("<h2>Products</h2>"))
        header_layout.addStretch()

        add_btn = QPushButton("Add Product")
        add_btn.clicked.connect(self.add_product)
        header_layout.addWidget(add_btn)

        layout.addLayout(header_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Name", "Date Added", "Total Bought", "Total Cost", "Current Stock"
        ])
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)

        self.setLayout(layout)

    def load_products(self):
        query = '''
            SELECT p.id, p.name, p.created_at,
                   COALESCE(SUM(sp.quantity), 0) as total_bought,
                   COALESCE(SUM(sp.subtotal), 0) as total_cost,
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
        products = self.db.execute_query(query)

        self.table.setRowCount(len(products))
        for row, product in enumerate(products):
            self.table.setItem(row, 0, QTableWidgetItem(product['name']))

            date_str = product['created_at'][:10].replace('-', '/')
            self.table.setItem(row, 1, QTableWidgetItem(date_str))

            bought = Decimal(str(product['total_bought'])).quantize(Decimal('0.01'))
            self.table.setItem(row, 2, QTableWidgetItem(f"{bought:,.2f}"))

            cost = Decimal(str(product['total_cost'])).quantize(Decimal('0.01'))
            self.table.setItem(row, 3, QTableWidgetItem(f"{cost:,.2f} DA"))

            stock = Decimal(str(product['current_stock'])).quantize(Decimal('0.01'))
            self.table.setItem(row, 4, QTableWidgetItem(f"{stock:,.2f}"))

    def add_product(self):
        name, ok = QInputDialog.getText(self, "Add Product", "Enter product name:")
        if ok and name.strip():
            try:
                self.db.execute_update('INSERT INTO products (name) VALUES (?)', (name.strip(),))
                self.load_products()
                QMessageBox.information(self, "Success", "Product added successfully")
            except:
                QMessageBox.warning(self, "Error", "Product name already exists")
