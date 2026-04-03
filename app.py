from flask import Flask, render_template, request, redirect, url_for, flash
import psycopg2
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "devkey123")

def get_db():
    return psycopg2.connect(os.environ["DATABASE_URL"])

@app.route("/")
def index():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM tasks;")
    total = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM tasks WHERE done = true;")
    done = cur.fetchone()[0]
    cur.close(); conn.close()
    return render_template("index.html", total=total, done=done, pending=total - done)

@app.route("/tasks")
def tasks():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM tasks ORDER BY id DESC;")
    all_tasks = cur.fetchall()
    cur.close(); conn.close()
    return render_template("tasks.html", tasks=all_tasks)

@app.route("/tasks/add", methods=["POST"])
def add_task():
    title = request.form.get("title")
    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO tasks (title, done) VALUES (%s, %s);", (title, False))
    conn.commit(); cur.close(); conn.close()
    flash("Task added!", "success")
    return redirect(url_for("tasks"))

@app.route("/tasks/toggle/<int:task_id>", methods=["POST"])
def toggle_task(task_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE tasks SET done = NOT done WHERE id = %s;", (task_id,))
    conn.commit(); cur.close(); conn.close()
    return redirect(url_for("tasks"))

@app.route("/tasks/delete/<int:task_id>", methods=["POST"])
def delete_task(task_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM tasks WHERE id = %s;", (task_id,))
    conn.commit(); cur.close(); conn.close()
    flash("Task deleted.", "success")
    return redirect(url_for("tasks"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)