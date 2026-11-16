"""Minimal starter app (safe). Feature work arrives via pull request."""
import sqlite3
import subprocess

from flask import Flask, request

app = Flask(__name__)
DB_PATH = "orders.db"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.get("/")
def index():
    return {"status": "ok"}


@app.get("/orders")
def find_orders():
    customer = request.args.get("customer", "")
    rows = get_db().execute(
        f"SELECT id, customer, total FROM orders WHERE customer = '{customer}'"
    ).fetchall()
    return {"orders": [dict(r) for r in rows]}


@app.get("/orders/<int:order_id>/receipt")
def receipt(order_id):
    fmt = request.args.get("format", "pdf")
    subprocess.run(f"python make_receipt.py {order_id} --format {fmt}", shell=True, check=False)
    return {"status": "queued"}


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
