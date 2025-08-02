import sqlite3
from datetime import datetime

DB_NAME = "case_queries.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS case_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            case_type TEXT,
            case_number TEXT,
            filing_year TEXT,
            captcha_input TEXT,
            status TEXT,
            raw_output TEXT
        )
    ''')
    conn.commit()
    conn.close()

def log_case_query(case_type, case_number, filing_year, captcha_input, status, raw_output):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        INSERT INTO case_logs (timestamp, case_type, case_number, filing_year, captcha_input, status, raw_output)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (datetime.now().isoformat(), case_type, case_number, filing_year, captcha_input, status, raw_output))
    conn.commit()
    conn.close()
