from flask import Flask, render_template_string, request, redirect
import sqlite3
import os

app = Flask(__name__)
DB_PATH = "cables.db"

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS cables (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                seq TEXT UNIQUE,
                point_a TEXT,
                point_b TEXT,
                description TEXT
            )
        ''')

def get_next_seq():
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("SELECT seq FROM cables ORDER BY id DESC LIMIT 1")
        last = cur.fetchone()
        if not last:
            return "A0001"
        num = int(last[0][1:]) + 1
        return f"A{num:04d}"

@app.route('/')
def index():
    with sqlite3.connect(DB_PATH) as conn:
        cables = conn.execute("SELECT * FROM cables").fetchall()
    return render_template_string(TEMPLATE, cables=cables)

@app.route('/add', methods=["POST"])
def add_cable():
    point_a = request.form['point_a']
    point_b = request.form['point_b']
    desc = request.form['description']
    seq = get_next_seq()
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("INSERT INTO cables (seq, point_a, point_b, description) VALUES (?, ?, ?, ?)", 
                     (seq, point_a, point_b, desc))
    return redirect('/')

@app.route('/edit/<seq>', methods=["POST"])
def edit_cable(seq):
    point_a = request.form['point_a']
    point_b = request.form['point_b']
    desc = request.form['description']
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("UPDATE cables SET point_a=?, point_b=?, description=? WHERE seq=?", 
                     (point_a, point_b, desc, seq))
    return redirect('/')

TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <title>Cable Records Demo</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="p-4">
    <div class="container">
        <h1>Cable Records (Demo)</h1>
        <form method="POST" action="/add" class="row g-3">
            <div class="col-md-3"><input name="point_a" class="form-control" placeholder="Point A" required></div>
            <div class="col-md-3"><input name="point_b" class="form-control" placeholder="Point B" required></div>
            <div class="col-md-4"><input name="description" class="form-control" placeholder="Description" required></div>
            <div class="col-md-2"><button class="btn btn-primary w-100">Add</button></div>
        </form>
        <hr>
        <table class="table table-bordered">
            <thead class="table-light"><tr><th>Seq</th><th>Point A</th><th>Point B</th><th>Description</th><th>Actions</th></tr></thead>
            <tbody>
                {% for row in cables %}
                <tr>
                    <form method="POST" action="/edit/{{ row[1] }}">
                        <td>{{ row[1] }}</td>
                        <td><input name="point_a" class="form-control" value="{{ row[2] }}"></td>
                        <td><input name="point_b" class="form-control" value="{{ row[3] }}"></td>
                        <td><input name="description" class="form-control" value="{{ row[4] }}"></td>
                        <td><button class="btn btn-sm btn-success">Save</button></td>
                    </form>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</body>
</html>
"""

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
