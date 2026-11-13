# -*- coding: utf-8 -*-
"""Database layer for Amlak Arash"""

import sqlite3
import os
from datetime import datetime
import jdatetime

DB_PATH = os.path.join(os.path.expanduser("~"), "AmlakArash", "amlak.db")


def ensure_dir():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)


def get_conn():
    ensure_dir()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def today_jalali():
    return jdatetime.date.today().strftime("%Y/%m/%d")


def init_db():
    conn = get_conn()
    c = conn.cursor()

    c.executescript("""
    CREATE TABLE IF NOT EXISTS agents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT,
        commission_percent REAL DEFAULT 40,
        active INTEGER DEFAULT 1
    );

    CREATE TABLE IF NOT EXISTS properties (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE,
        title TEXT NOT NULL,
        property_type TEXT,
        deal_type TEXT,
        price REAL DEFAULT 0,
        rent_deposit REAL DEFAULT 0,
        rent_monthly REAL DEFAULT 0,
        area REAL DEFAULT 0,
        rooms INTEGER DEFAULT 0,
        floor TEXT,
        year_built INTEGER,
        address TEXT,
        city TEXT DEFAULT 'اصفهان',
        neighborhood TEXT,
        status TEXT DEFAULT 'فعال',
        owner_name TEXT,
        owner_phone TEXT,
        is_colleague INTEGER DEFAULT 0,
        colleague_name TEXT,
        colleague_phone TEXT,
        colleague_share REAL DEFAULT 0,
        visit_date TEXT,
        visit_time TEXT,
        visit_note TEXT,
        source TEXT,
        description TEXT,
        agent_id INTEGER,
        created_at TEXT,
        updated_at TEXT,
        FOREIGN KEY (agent_id) REFERENCES agents(id)
    );

    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE,
        name TEXT NOT NULL,
        phone TEXT,
        phone2 TEXT,
        request_type TEXT,
        property_type TEXT,
        deal_type TEXT,
        budget_min REAL DEFAULT 0,
        budget_max REAL DEFAULT 0,
        rent_deposit_min REAL DEFAULT 0,
        rent_deposit_max REAL DEFAULT 0,
        rent_monthly_min REAL DEFAULT 0,
        rent_monthly_max REAL DEFAULT 0,
        area_min REAL DEFAULT 0,
        area_max REAL DEFAULT 0,
        rooms INTEGER DEFAULT 0,
        preferred_regions TEXT,
        status TEXT DEFAULT 'جدید',
        priority TEXT DEFAULT 'عادی',
        next_followup TEXT,
        agent_id INTEGER,
        source TEXT,
        notes TEXT,
        created_at TEXT,
        updated_at TEXT,
        FOREIGN KEY (agent_id) REFERENCES agents(id)
    );

    CREATE TABLE IF NOT EXISTS contracts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE,
        property_id INTEGER,
        customer_id INTEGER,
        deal_type TEXT,
        total_amount REAL DEFAULT 0,
        commission_percent REAL DEFAULT 0.5,
        commission_amount REAL DEFAULT 0,
        agent_share REAL DEFAULT 0,
        agency_share REAL DEFAULT 0,
        colleague_share REAL DEFAULT 0,
        received_amount REAL DEFAULT 0,
        status TEXT DEFAULT 'فعال',
        contract_date TEXT,
        start_date TEXT,
        end_date TEXT,
        agent_id INTEGER,
        notes TEXT,
        created_at TEXT,
        FOREIGN KEY (property_id) REFERENCES properties(id),
        FOREIGN KEY (customer_id) REFERENCES customers(id),
        FOREIGN KEY (agent_id) REFERENCES agents(id)
    );

    CREATE TABLE IF NOT EXISTS contacts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT,
        phone2 TEXT,
        category TEXT DEFAULT 'متفرقه',
        company TEXT,
        address TEXT,
        notes TEXT,
        created_at TEXT
    );

    CREATE TABLE IF NOT EXISTS notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        content TEXT,
        pinned INTEGER DEFAULT 0,
        created_at TEXT,
        updated_at TEXT
    );

    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        due_date TEXT,
        due_time TEXT DEFAULT '09:00',
        is_done INTEGER DEFAULT 0,
        related_type TEXT,
        related_id INTEGER,
        created_at TEXT
    );

    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    );

    CREATE TABLE IF NOT EXISTS followups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        note TEXT,
        next_date TEXT,
        created_at TEXT,
        FOREIGN KEY (customer_id) REFERENCES customers(id)
    );
    """)

    defaults = {
        "commission_sale": "0.5",
        "commission_rent_factor": "25",
        "agency_name": "املاک آرش",
        "city": "اصفهان",
    }
    for k, v in defaults.items():
        c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (k, v))

    c.execute("SELECT COUNT(*) FROM agents")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO agents (name, phone, commission_percent) VALUES (?, ?, ?)",
                  ("مشاور ۱", "", 40))

    conn.commit()
    conn.close()


def next_code(prefix, table):
    conn = get_conn()
    c = conn.cursor()
    c.execute(f"SELECT code FROM {table} WHERE code LIKE ? ORDER BY id DESC LIMIT 1", (f"{prefix}%",))
    row = c.fetchone()
    conn.close()
    if row and row["code"]:
        try:
            num = int(row["code"].replace(prefix, "")) + 1
        except:
            num = 1
    else:
        num = 1
    return f"{prefix}{num:04d}"


def get_setting(key, default=""):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT value FROM settings WHERE key=?", (key,))
    row = c.fetchone()
    conn.close()
    return row["value"] if row else default


def set_setting(key, value):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, str(value)))
    conn.commit()
    conn.close()
