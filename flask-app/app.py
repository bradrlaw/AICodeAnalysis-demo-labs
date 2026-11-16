"""Minimal starter app (safe). Feature work arrives via pull request."""
from flask import Flask

app = Flask(__name__)


@app.get("/")
def index():
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
