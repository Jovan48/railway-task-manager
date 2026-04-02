from flask import Flask, request, jsonify
import psycopg2
import os

app = Flask(__name__)

def get_db():
    return psycopg2.connect(os.environ["DATABASE_URL"])

@app.route("/")
def index():
    return jsonify({"message": "Task Manager API v2 - CI/CD works!"})

@app.route("/tasks", methods=["GET"])
def get_tasks():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM tasks;")
    tasks = cur.fetchall()
    cur.close(); conn.close()
    return jsonify([{"id": t[0], "title": t[1], "done": t[2]} for t in tasks])

@app.route("/tasks", methods=["POST"])
def create_task():
    data = request.get_json()
    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO tasks (title, done) VALUES (%s, %s) RETURNING id;",
                (data["title"], False))
    new_id = cur.fetchone()[0]
    conn.commit(); cur.close(); conn.close()
    return jsonify({"id": new_id, "title": data["title"], "done": False}), 201

@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    data = request.get_json()
    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE tasks SET title=%s, done=%s WHERE id=%s;",
                (data["title"], data["done"], task_id))
    conn.commit(); cur.close(); conn.close()
    return jsonify({"message": "Task updated"})

@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM tasks WHERE id=%s;", (task_id,))
    conn.commit(); cur.close(); conn.close()
    return jsonify({"message": "Task deleted"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


