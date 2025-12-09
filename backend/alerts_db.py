import sqlite3
import datetime

DB_NAME = "alerts.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            crop TEXT NOT NULL,
            target_price REAL NOT NULL,
            condition TEXT NOT NULL, -- 'Above' or 'Below'
            contact TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def add_alert(crop, target_price, condition, contact):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO alerts (crop, target_price, condition, contact) VALUES (?, ?, ?, ?)',
                   (crop, target_price, condition, contact))
    conn.commit()
    alert_id = cursor.lastrowid
    conn.close()
    return alert_id

def get_alerts():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM alerts')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def delete_alert(alert_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM alerts WHERE id = ?', (alert_id,))
    conn.commit()
    conn.close()
