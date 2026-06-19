"""
数据库入门 — SQLite 客户管理
============================
用 SQLite 存数据：客户信息、订单记录、交付历史
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = "data/business.db"


def get_conn():
    """获取数据库连接"""
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """初始化数据库表"""
    conn = get_conn()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            contact TEXT,
            source TEXT,
            note TEXT,
            created_at TEXT DEFAULT (datetime('now', 'localtime'))
        );

        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL,
            service_type TEXT NOT NULL,
            product_name TEXT,
            style TEXT DEFAULT '朋友圈',
            count INTEGER DEFAULT 3,
            price REAL,
            status TEXT DEFAULT 'pending',
            created_at TEXT DEFAULT (datetime('now', 'localtime')),
            delivered_at TEXT,
            FOREIGN KEY (client_id) REFERENCES clients(id)
        );

        CREATE TABLE IF NOT EXISTS deliveries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            content TEXT,
            delivered_at TEXT DEFAULT (datetime('now', 'localtime')),
            FOREIGN KEY (order_id) REFERENCES orders(id)
        );
    """)
    conn.commit()
    conn.close()
    print("✅ 数据库初始化完成")


def add_client(name, contact="", source="", note=""):
    """添加客户"""
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO clients (name, contact, source, note) VALUES (?, ?, ?, ?)",
        (name, contact, source, note)
    )
    conn.commit()
    client_id = cursor.lastrowid
    conn.close()
    print(f"✅ 已添加客户：{name}（ID: {client_id}）")
    return client_id


def add_order(client_id, service_type, product_name="", style="朋友圈", count=3, price=0):
    """添加订单"""
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO orders (client_id, service_type, product_name, style, count, price)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (client_id, service_type, product_name, style, count, price)
    )
    conn.commit()
    order_id = cursor.lastrowid
    conn.close()
    print(f"✅ 已创建订单（ID: {order_id}）")
    return order_id


def list_clients():
    """列出所有客户"""
    conn = get_conn()
    cursor = conn.cursor()
    rows = cursor.execute("SELECT * FROM clients ORDER BY created_at DESC").fetchall()
    conn.close()
    if not rows:
        print("📭 暂无客户记录")
        return
    print(f"\n📋 客户列表（共 {len(rows)} 人）")
    print("-" * 60)
    for r in rows:
        print(f"  [{r['id']}] {r['name']} | {r['contact']} | {r['source']} | {r['created_at']}")


def list_orders(status=None):
    """列出订单"""
    conn = get_conn()
    cursor = conn.cursor()
    if status:
        rows = cursor.execute(
            "SELECT o.*, c.name FROM orders o JOIN clients c ON o.client_id=c.id WHERE o.status=? ORDER BY o.created_at DESC",
            (status,)
        ).fetchall()
    else:
        rows = cursor.execute(
            "SELECT o.*, c.name FROM orders o JOIN clients c ON o.client_id=c.id ORDER BY o.created_at DESC"
        ).fetchall()
    conn.close()
    if not rows:
        print("📭 暂无订单")
        return
    print(f"\n📋 订单列表（共 {len(rows)} 单）")
    print("-" * 70)
    for r in rows:
        status_icon = {"pending": "⏳", "done": "✅", "paid": "💰"}.get(r["status"], "❓")
        print(f"  {status_icon} [{r['id']}] {r['name']} | {r['service_type']} | ¥{r['price']} | {r['status']}")


def summary():
    """经营概况"""
    conn = get_conn()
    cursor = conn.cursor()
    client_count = cursor.execute("SELECT COUNT(*) FROM clients").fetchone()[0]
    order_count = cursor.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    pending = cursor.execute("SELECT COUNT(*) FROM orders WHERE status='pending'").fetchone()[0]
    total_revenue = cursor.execute("SELECT COALESCE(SUM(price), 0) FROM orders WHERE status='paid'").fetchone()[0]
    conn.close()

    print(f"\n📊 经营概况")
    print("=" * 30)
    print(f"👥 客户数：{client_count}")
    print(f"📦 订单数：{order_count}（待处理：{pending}）")
    print(f"💰 总收入：¥{total_revenue}")


if __name__ == "__main__":
    import sys
    init_db()
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "clients":
            list_clients()
        elif cmd == "orders":
            status = sys.argv[2] if len(sys.argv) > 2 else None
            list_orders(status)
        elif cmd == "summary":
            summary()
        elif cmd == "add_client" and len(sys.argv) > 2:
            add_client(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "")
        else:
            print("用法: python src/database.py [clients|orders|summary|add_client]")
    else:
        # 演示
        init_db()
        summary()
