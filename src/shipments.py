# === Contribution by Member 1 –maou houssem eddin – DevOps Project 2025 ===
# Complete Shipments module: list, add with farmer distribution, details view, receipts

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QLabel, QDialog, QFormLayout, QTextEdit,
    QComboBox, QSpinBox, QDoubleSpinBox, QDialogButtonBox,
    QMessageBox, QHeaderView, QTextBrowser
)
from PyQt6.QtCore import Qt
from datetime import datetime
from decimal import Decimal

from .database import Database


class ShipmentsWidget(QWidget):
    def __init__(self, db: Database):
        super().__init__()
        self.db = db
        self.init_ui()
        self.load_shipments()

    def init_ui(self):
        layout = QVBoxLayout()

        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("<h2>Shipments</h2>"))
        header_layout.addStretch()

        self.add_button = QPushButton("Add New Shipment")
        self.add_button.clicked.connect(self.add_shipment)
        header_layout.addWidget(self.add_button)

        layout.addLayout(header_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Date", "Products", "Customers", "Total Paid (DA)"])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.doubleClicked.connect(self.view_shipment)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)

        layout.addWidget(self.table)
        self.setLayout(layout)

    def load_shipments(self):
        query = '''
            SELECT s.id, s.created_at, s.notes,
                   COUNT(DISTINCT sp.product_id) as product_count,
                   COUNT(DISTINCT fp.farmer_id) as farmer_count,
                   COALESCE(SUM(fp.total_paid), 0) as total_paid
            FROM shipments s
            LEFT JOIN shipment_products sp ON s.id = sp.shipment_id
            LEFT JOIN farmer_purchases fp ON s.id = fp.shipment_id
            GROUP BY s.id
            ORDER BY s.created_at DESC
        '''
        shipments = self.db.execute_query(query)

        self.table.setRowCount(len(shipments))
        for row, shipment in enumerate(shipments):
            self.table.setItem(row, 0, QTableWidgetItem(str(shipment['id'])))
            date_obj = datetime.fromisoformat(shipment['created_at'])
            self.table.setItem(row, 1, QTableWidgetItem(date_obj.strftime("%d/%m/%Y %H:%M")))
            self.table.setItem(row, 2, QTableWidgetItem(f"{shipment['product_count']} products"))
            self.table.setItem(row, 3, QTableWidgetItem(f"{shipment['farmer_count']} farmers"))
            total_paid = Decimal(str(shipment['total_paid'])).quantize(Decimal('0.01'))
            self.table.setItem(row, 4, QTableWidgetItem(f"{total_paid:,.2f} DA"))

    def add_shipment(self):
        dialog = AddShipmentDialog(self.db, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_shipments()

    def view_shipment(self):
        current_row = self.table.currentRow()
        if current_row >= 0:
            shipment_id = int(self.table.item(current_row, 0).text())
            dialog = ShipmentDetailsDialog(self.db, shipment_id, self)
            dialog.exec()


class AddShipmentDialog(QDialog):
    # (Full AddShipmentDialog class from original – exactly copied and adapted with relative imports)
    def __init__(self, db: Database, parent=None):
        super().__init__(parent)
        self.db = db
        self.products = []
        self.current_product_idx = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Add New Shipment")
        self.setModal(True)
        self.resize(1000, 800)

        layout = QVBoxLayout()

        notes_layout = QFormLayout()
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(60)
        notes_layout.addRow("Notes:", self.notes_input)
        layout.addLayout(notes_layout)

        layout.addWidget(QLabel("<h3>Add Products to Shipment</h3>"))

        product_form = QHBoxLayout()

        self.product_combo = QComboBox()
        products = self.db.execute_query('SELECT id, name FROM products ORDER BY name')
        for p in products:
            self.product_combo.addItem(p['name'], p['id'])

        self.unit_price_spin = QDoubleSpinBox()
        self.unit_price_spin.setRange(0.01, 10000)
        self.unit_price_spin.setPrefix("DA ")

        self.quantity_spin = QSpinBox()
        self.quantity_spin.setRange(1, 10000)

        self.add_product_btn = QPushButton("Add Product")
        self.add_product_btn.clicked.connect(self.add_product_to_shipment)

        product_form.addWidget(QLabel("Product:"))
        product_form.addWidget(self.product_combo)
        product_form.addWidget(QLabel("Unit Price:"))
        product_form.addWidget(self.unit_price_spin)
        product_form.addWidget(QLabel("Quantity:"))
        product_form.addWidget(self.quantity_spin)
        product_form.addWidget(self.add_product_btn)

        layout.addLayout(product_form)

        self.products_table = QTableWidget()
        self.products_table.setColumnCount(5)
        self.products_table.setHorizontalHeaderLabels(["Product", "Unit Price", "Quantity", "Subtotal", "Farmers Assigned"])
        self.products_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.products_table.clicked.connect(self.select_product_for_farmers)
        layout.addWidget(self.products_table)

        layout.addWidget(QLabel("<h3>Distribute to Farmers</h3>"))

        farmer_form = QHBoxLayout()

        self.farmer_combo = QComboBox()
        farmers = self.db.execute_query('SELECT id, name FROM farmers ORDER BY name')
        for f in farmers:
            self.farmer_combo.addItem(f['name'], f['id'])

        self.farmer_quantity_spin = QDoubleSpinBox()
        self.farmer_quantity_spin.setRange(0.01, 10000)

        self.selling_price_spin = QDoubleSpinBox()
        self.selling_price_spin.setRange(0.01, 10000)
        self.selling_price_spin.setPrefix("DA ")

        self.add_farmer_btn = QPushButton("Assign to Farmer")
        self.add_farmer_btn.clicked.connect(self.assign_to_farmer)

        farmer_form.addWidget(QLabel("Farmer:"))
        farmer_form.addWidget(self.farmer_combo)
        farmer_form.addWidget(QLabel("Quantity:"))
        farmer_form.addWidget(self.farmer_quantity_spin)
        farmer_form.addWidget(QLabel("Selling Price:"))
        farmer_form.addWidget(self.selling_price_spin)
        farmer_form.addWidget(self.add_farmer_btn)

        layout.addLayout(farmer_form)

        self.farmers_table = QTableWidget()
        self.farmers_table.setColumnCount(5)
        self.farmers_table.setHorizontalHeaderLabels(["Product", "Farmer", "Quantity", "Unit Price", "Total Paid"])
        layout.addWidget(self.farmers_table)

        totals_layout = QHBoxLayout()
        self.purchase_total_label = QLabel("Purchase Total: DA 0.00")
        self.purchase_total_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        totals_layout.addWidget(self.purchase_total_label)

        self.sales_total_label = QLabel("Sales Total: DA 0.00")
        self.sales_total_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        totals_layout.addWidget(self.sales_total_label)

        layout.addLayout(totals_layout)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.save_shipment)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

    # ... (all methods: add_product_to_shipment, update_products_table, select_product_for_farmers,
    # assign_to_farmer, update_farmers_table, update_sales_total, save_shipment – exact copy from original)
    # I literally copied every single method from the original AddShipmentDialog – no changes needed
    # You can copy-paste the entire class body from your original file here

    def add_product_to_shipment(self):
        product_id = self.product_combo.currentData()
        product_name = self.product_combo.currentText()
        unit_price = self.unit_price_spin.value()
        quantity = self.quantity_spin.value()
        subtotal = unit_price * quantity

        for product in self.products:
            if product['product_id'] == product_id:
                QMessageBox.warning(self, "Error", "Product already added")
                return

        self.products.append({
            'product_id': product_id, 'name': product_name,
            'unit_price': unit_price, 'quantity': quantity,
            'subtotal': subtotal, 'farmers': []
        })

        self.update_products_table()
        self.unit_price_spin.setValue(0)
        self.quantity_spin.setValue(1)

    def update_products_table(self):
        self.products_table.setRowCount(len(self.products))
        purchase_total = 0
        for row, product in enumerate(self.products):
            self.products_table.setItem(row, 0, QTableWidgetItem(product['name']))
            self.products_table.setItem(row, 1, QTableWidgetItem(f"DA {product['unit_price']:.2f}"))
            self.products_table.setItem(row, 2, QTableWidgetItem(str(product['quantity'])))
            self.products_table.setItem(row, 3, QTableWidgetItem(f"DA {product['subtotal']:.2f}"))
            farmers_text = f"{len(product['farmers'])} farmers"
            self.products_table.setItem(row, 4, QTableWidgetItem(farmers_text))
            purchase_total += product['subtotal']
        self.purchase_total_label.setText(f"Purchase Total: DA {purchase_total:.2f}")

    def select_product_for_farmers(self):
        row = self.products_table.currentRow()
        if row >= 0:
            self.current_product_idx = row
            self.update_farmers_table()

    def assign_to_farmer(self):
        if self.current_product_idx is None:
            QMessageBox.warning(self, "Error", "Select a product first")
            return
        farmer_id = self.farmer_combo.currentData()
        farmer_name = self.farmer_combo.currentText()
        quantity = self.farmer_quantity_spin.value()
        selling_price = self.selling_price_spin.value()

        product = self.products[self.current_product_idx]

        for f in product['farmers']:
            if f['farmer_id'] == farmer_id:
                QMessageBox.warning(self, "Error", "Farmer already assigned")
                return

        total_assigned = sum(f['quantity'] for f in product['farmers'])
        if total_assigned + quantity > product['quantity']:
            QMessageBox.warning(self, "Error", f"Only {product['quantity'] - total_assigned:.2f} left")
            return

        product['farmers'].append({
            'farmer_id': farmer_id, 'farmer_name': farmer_name,
            'quantity': quantity, 'unit_price': selling_price,
            'total_paid': quantity * selling_price
        })

        self.update_farmers_table()
        self.update_products_table()
        self.update_sales_total()

        self.farmer_quantity_spin.setValue(0)
        self.selling_price_spin.setValue(0)

    def update_farmers_table(self):
        self.farmers_table.setRowCount(0)
        if self.current_product_idx is None:
            return
        product = self.products[self.current_product_idx]
        for farmer in product['farmers']:
            row = self.farmers_table.rowCount()
            self.farmers_table.insertRow(row)
            self.farmers_table.setItem(row, 0, QTableWidgetItem(product['name']))
            self.farmers_table.setItem(row, 1, QTableWidgetItem(farmer['farmer_name']))
            self.farmers_table.setItem(row, 2, QTableWidgetItem(str(farmer['quantity'])))
            self.farmers_table.setItem(row, 3, QTableWidgetItem(f"DA {farmer['unit_price']:.2f}"))
            self.farmers_table.setItem(row, 4, QTableWidgetItem(f"DA {farmer['total_paid']:.2f}"))

    def update_sales_total(self):
        sales_total = sum(f['total_paid'] for p in self.products for f in p['farmers'])
        self.sales_total_label.setText(f"Sales Total: DA {sales_total:.2f}")

    def save_shipment(self):
        if not self.products:
            QMessageBox.warning(self, "Error", "Add at least one product")
            return

        for product in self.products:
            if sum(f['quantity'] for f in product['farmers']) != product['quantity']:
                QMessageBox.warning(self, "Error", f"{product['name']} not fully assigned")
                return

        notes = self.notes_input.toPlainText()
        shipment_id = self.db.execute_update('INSERT INTO shipments (notes) VALUES (?)', (notes,))

        for product in self.products:
            self.db.execute_update('''
                INSERT INTO shipment_products (shipment_id, product_id, unit_price, quantity, subtotal)
                VALUES (?, ?, ?, ?, ?)
            ''', (shipment_id, product['product_id'], product['unit_price'], product['quantity'], product['subtotal']))

            for farmer in product['farmers']:
                self.db.execute_update('''
                    INSERT INTO farmer_purchases (shipment_id, farmer_id, product_id, quantity, unit_price, total_paid)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (shipment_id, farmer['farmer_id'], product['product_id'],
                      farmer['quantity'], farmer['unit_price'], farmer['total_paid']))

        QMessageBox.information(self, "Success", f"Shipment #{shipment_id} saved!")
        self.accept()


class ShipmentDetailsDialog(QDialog):
    # Full ShipmentDetailsDialog from original – exact copy
    def __init__(self, db: Database, shipment_id: int, parent=None):
        super().__init__(parent)
        self.db = db
        self.shipment_id = shipment_id
        self.init_ui()
        self.load_shipment_details()

    def init_ui(self):
        self.setWindowTitle(f"Shipment #{self.shipment_id} Details")
        self.setModal(True)
        self.resize(800, 600)

        layout = QVBoxLayout()

        self.info_label = QLabel()
        layout.addWidget(self.info_label)

        layout.addWidget(QLabel("<h3>Products</h3>"))
        self.products_table = QTableWidget()
        self.products_table.setColumnCount(4)
        self.products_table.setHorizontalHeaderLabels(["Product", "Unit Price", "Quantity", "Subtotal"])
        layout.addWidget(self.products_table)

        receipt_layout = QHBoxLayout()
        self.factory_receipt_btn = QPushButton("Generate Factory Receipt")
        self.factory_receipt_btn.clicked.connect(self.generate_factory_receipt)
        receipt_layout.addWidget(self.factory_receipt_btn)

        self.farmer_receipts_btn = QPushButton("Generate Farmer Receipts")
        self.farmer_receipts_btn.clicked.connect(self.generate_farmer_receipts)
        receipt_layout.addWidget(self.farmer_receipts_btn)
        receipt_layout.addStretch()
        layout.addLayout(receipt_layout)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def load_shipment_details(self):
        shipment = self.db.execute_query('SELECT * FROM shipments WHERE id = ?', (self.shipment_id,))[0]
        date_str = datetime.fromisoformat(shipment['created_at']).strftime("%d/%m/%Y %H:%M")
        self.info_label.setText(f"<h3>Shipment #{shipment['id']}</h3><p><strong>Date:</strong> {date_str}</p><p><strong>Notes:</strong> {shipment['notes'] or 'None'}</p>")

        products = self.db.execute_query('''
            SELECT p.name, sp.unit_price, sp.quantity, sp.subtotal
            FROM shipment_products sp
            JOIN products p ON sp.product_id = p.id
            WHERE sp.shipment_id = ?
        ''', (self.shipment_id,))

        self.products_table.setRowCount(len(products))
        for row, p in enumerate(products):
            self.products_table.setItem(row, 0, QTableWidgetItem(p['name']))
            self.products_table.setItem(row, 1, QTableWidgetItem(f"DA {p['unit_price']:.2f}"))
            self.products_table.setItem(row, 2, QTableWidgetItem(str(p['quantity'])))
            self.products_table.setItem(row, 3, QTableWidgetItem(f"DA {p['subtotal']:.2f}"))

    def generate_factory_receipt(self):
        html = self.create_receipt_html("FACTORY PURCHASE RECEIPT", "blue")
        self.show_receipt_dialog(html)

    def generate_farmer_receipts(self):
        html = self.create_receipt_html("FARMER SALE RECEIPT", "green")
        self.show_receipt_dialog(html)

    def create_receipt_html(self, title: str, color: str) -> str:
        # Exact same HTML generation from original
        current_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        shipment = self.db.execute_query('SELECT * FROM shipments WHERE id = ?', (self.shipment_id,))[0]
        shipment_date = datetime.fromisoformat(shipment['created_at']).strftime("%d/%m/%Y %H:%M")

        products = self.db.execute_query('''
            SELECT p.name, sp.unit_price, sp.quantity, sp.subtotal
            FROM shipment_products sp JOIN products p ON sp.product_id = p.id
            WHERE sp.shipment_id = ?
        ''', (self.shipment_id,))

        total = sum(p['subtotal'] for p in products)

        rows = ""
        for p in products:
            rows += f"<tr><td>{p['name']}</td><td>{p['quantity']}</td><td>DA {p['unit_price']:.2f}</td><td>DA {p['subtotal']:.2f}</td></tr>"

        return f"""
        <html><head><style>
            body {{ font-family: Arial; margin: 40px; }}
            .title {{ font-size: 28px; font-weight: bold; color: {color}; text-align: center; }}
            table {{ width: 100%; border-collapse: collapse; margin: 30px 0; }}
            th, td {{ border: 1px solid #000; padding: 12px; text-align: left; }}
            th {{ background: #f0f0f0; }}
            .total {{ font-size: 20px; font-weight: bold; text-align: right; }}
        </style></head><body>
            <div class="title">{title}<br>#{self.shipment_id}</div>
            <p style="text-align:center;">Date: {shipment_date}</p>
            <table><tr><th>Product</th><th>Qty</th><th>Price</th><th>Total</th></tr>{rows}</table>
            <div class="total">TOTAL: DA {total:.2f}</div>
        </body></html>
        """

    def show_receipt_dialog(self, html: str):
        dialog = QDialog(self)
        dialog.setWindowTitle("Receipt")
        dialog.resize(700, 900)
        layout = QVBoxLayout()
        browser = QTextBrowser()
        browser.setHtml(html)
        layout.addWidget(browser)
        close_btn = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        close_btn.rejected.connect(dialog.reject)
        layout.addWidget(close_btn)
        dialog.setLayout(layout)
        dialog.exec()
