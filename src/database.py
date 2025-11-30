import sqlite3
import hashlib
import logging
from datetime import datetime
from typing import List, Dict, Any


class Database:
    def __init__(self, db_path: str = "shipments.db"):
        self.db_path = db_path
        self.init_database()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        conn.row_factory = sqlite3.Row
        return conn

    def init_database(self):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # All tables (exact same as original)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS farmers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS shipments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    notes TEXT
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS shipment_products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    shipment_id INTEGER REFERENCES shipments(id) ON DELETE CASCADE,
                    product_id INTEGER REFERENCES products(id),
                    unit_price REAL NOT NULL,
                    quantity INTEGER NOT NULL,
                    subtotal REAL
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS farmer_purchases (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    shipment_id INTEGER REFERENCES shipments(id) ON DELETE CASCADE,
                    farmer_id INTEGER REFERENCES farmers(id),
                    product_id INTEGER REFERENCES products(id),
                    quantity REAL NOT NULL,
                    unit_price REAL NOT NULL,
                    total_paid REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transfers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    from_farmer_id INTEGER REFERENCES farmers(id),
                    to_farmer_id INTEGER REFERENCES farmers(id),
                    product_id INTEGER REFERENCES products(id),
                    quantity REAL NOT NULL,
                    note TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS returns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    farmer_id INTEGER REFERENCES farmers(id),
                    product_id INTEGER REFERENCES products(id),
                    quantity REAL NOT NULL,
                    refund_amount REAL,
                    note TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL
                )
            ''')

            # Indexes and default admin + seed data (exact same as original)
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_shipment_products_shipment_id ON shipment_products(shipment_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_farmer_purchases_shipment_id ON farmer_purchases(shipment_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_farmer_purchases_farmer_id ON farmer_purchases(farmer_id)')

            password_hash = hashlib.sha256("password123".encode()).hexdigest()
            cursor.execute('INSERT OR IGNORE INTO users (username, password_hash) VALUES (?, ?)', ('admin', password_hash))

            cursor.execute('SELECT COUNT(*) FROM products')
            if cursor.fetchone()[0] == 0:
                products = ['Tomato', 'Potato', 'Onion']
                for p in products:
                    cursor.execute('INSERT INTO products (name) VALUES (?)', (p,))
                farmers = ['Farmer A', 'Farmer B', 'Farmer C']
                for f in farmers:
                    cursor.execute('INSERT INTO farmers (name) VALUES (?)', (f,))
                cursor.execute('INSERT INTO shipments (notes) VALUES (?)', ('Sample shipment',))
                shipment_id = cursor.lastrowid
                cursor.execute('INSERT INTO shipment_products (shipment_id, product_id, unit_price, quantity, subtotal) VALUES (?, 1, 50.00, 100, 5000.00)', (shipment_id,))
                cursor.execute('INSERT INTO farmer_purchases (shipment_id, farmer_id, product_id, quantity, unit_price, total_paid) VALUES (?, 1, 1, 50, 65.00, 3250.00)', (shipment_id,))

            conn.commit()
            conn.close()
        except Exception as e:
            logging.error(f"Database initialization error: {e}")
            raise

    def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results

    def execute_update(self, query: str, params: tuple = ()) -> int:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        last_row_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return last_row_id
