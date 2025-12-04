from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QLabel, QHeaderView,
    QMessageBox, QInputDialog
)
from PyQt6.QtCore import Qt
from database import Database
from decimal import Decimal

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

        self.add_button = QPushButton("Add Product")
        self.add_button.clicked.connect(self.add_product)
        header_layout.addWidget(self.add_button)
        layout.addLayout(header_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Name", "Date Added", "Total Bought", "Total Cost", "Current Stock"
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.doubleClicked.connect(self.view_product)
        layout.addWidget(self.table)
        self.setLayout(layout)

    def load_products(self):
        query = '''
            SELECT p.id, p.name, p.created_at,
                   COALESCE(SUM(sp.quantity), 0) as total_bought,
                   COALESCE(SUM(sp.subtotal), 0) as total_cost,
                   COALESCE(SUM(sp.quantity), 0) - COALESCE(SUM(fp.quantity), 0) - COALESCE(SUM(r.quantity), 0) as current_stock
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

            date_obj = datetime.fromisoformat(product['created_at'])
            self.table.setItem(row, 1, QTableWidgetItem(date_obj.strftime("%d/%m/%Y")))

            self.table.setItem(row, 2, QTableWidgetItem(f"{Decimal(str(product['total_bought'])):,.2f}"))
            self.table.setItem(row, 3, QTableWidgetItem(f"{Decimal(str(product['total_cost'])):,.2f} DA"))
            self.table.setItem(row, 4, QTableWidgetItem(f"{Decimal(str(product['current_stock'])):,.2f}"))

    def add_product(self):
        name, ok = QInputDialog.getText(self, "Add Product", "Enter product name:")
        if ok and name:
            try:
                self.db.execute_update('INSERT INTO products (name) VALUES (?)', (name,))
                self.load_products()
                QMessageBox.information(self, "Success", "Product added")
            except:
                QMessageBox.warning(self, "Error", "Failed (name exists?)")

    def view_product(self):
        pass  # optional details
