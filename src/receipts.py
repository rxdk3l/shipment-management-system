# === Contribution by Member 3 – radjab beddiar – DevOps Project 2025 ===
# Receipt generation (factory, farmer, shipment)

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGroupBox, QPushButton, QTextBrowser
from PyQt6.QtGui import QFont

class ReceiptsWidget(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        layout = QVBoxLayout()
        layout.addWidget(QLabel("<h2>Receipts</h2>"))

        group = QGroupBox("Generate Sample Receipts")
        g_layout = QVBoxLayout()
        QPushButton("Factory Purchase Receipt", clicked=self.factory).setParent(self)
        g_layout.addWidget(QPushButton("Factory Purchase Receipt", clicked=self.factory))
        g_layout.addWidget(QPushButton("Farmer Sale Receipt", clicked=self.farmer))
        g_layout.addWidget(QPushButton("Shipment Receipt", clicked=self.shipment))
        group.setLayout(g_layout)
        layout.addWidget(group)

        self.preview = QTextBrowser()
        layout.addWidget(self.preview)
        self.setLayout(layout)

    def factory(self):
        self.preview.setHtml(self.html_template("FACTORY PURCHASE RECEIPT", "#0066cc"))

    def farmer(self):
        self.preview.setHtml(self.html_template("FARMER SALE RECEIPT", "#00aa00"))

    def shipment(self):
        self.preview.setHtml(self.html_template("SHIPMENT RECEIPT", "#ff6600"))

    def html_template(self, title, color):
        from datetime import datetime
        now = datetime.now().strftime("%d/%m/%Y %H:%M")
        return f"""
        <html><head><style>
        body {{font-family: Arial; margin: 40px;}}
        .title {{font-size: 28px; color: {color}; text-align: center; font-weight: bold;}}
        table {{width: 100%; border-collapse: collapse; margin: 30px 0;}}
        th, td {{border: 1px solid #000; padding: 12px;}}
        th {{background: #f0f0f0;}}
        .total {{font-size: 20px; font-weight: bold; text-align: right;}}
        </style></head><body>
        <div class="title">{title}</div>
        <p style="text-align:center;">Generated: {now}</p>
        <table>
            <tr><th>Item</th><th>Qty</th><th>Price</th><th>Subtotal</th></tr>
            <tr><td>Sample Product</td><td>100</td><td>DA 50.00</td><td>DA 5,000.00</td></tr>
        </table>
        <div class="total">Total: DA 5,000.00</div>
        </body></html>
        """
