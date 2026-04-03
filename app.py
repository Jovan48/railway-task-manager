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
    cur.execute("SELECT * FROM tasks ORDER BY id DESC;")
    all_tasks = cur.fetchall()
    cur.execute("SELECT * FROM tasks WHERE done = false ORDER BY due_date ASC NULLS LAST;")
    pending_tasks = cur.fetchall()
    cur.execute("SELECT * FROM tasks WHERE done = true ORDER BY id DESC;")
    done_tasks = cur.fetchall()
    cur.close(); conn.close()
    return render_template("index.html",
        total=total, done=done, pending=total - done,
        all_tasks=all_tasks, pending_tasks=pending_tasks, done_tasks=done_tasks)

@app.route("/tasks")
def tasks():
    conn = get_db()
    cur = conn.cursor()
    search = request.args.get("search", "")
    priority = request.args.get("priority", "")
    category = request.args.get("category", "")
    status = request.args.get("status", "")
    query = "SELECT * FROM tasks WHERE 1=1"
    params = []
    if search:
        query += " AND title ILIKE %s"
        params.append(f"%{search}%")
    if priority:
        query += " AND priority = %s"
        params.append(priority)
    if category:
        query += " AND category = %s"
        params.append(category)
    if status == "done":
        query += " AND done = true"
    elif status == "pending":
        query += " AND done = false"
    query += " ORDER BY CASE priority WHEN 'high' THEN 1 WHEN 'medium' THEN 2 WHEN 'low' THEN 3 END, due_date ASC NULLS LAST"
    cur.execute(query, params)
    all_tasks = cur.fetchall()
    cur.execute("SELECT DISTINCT category FROM tasks WHERE category IS NOT NULL ORDER BY category;")
    categories = [row[0] for row in cur.fetchall()]
    cur.close(); conn.close()
    return render_template("tasks.html", tasks=all_tasks, categories=categories,
        search=search, priority=priority, category=category, status=status)

@app.route("/tasks/add", methods=["POST"])
def add_task():
    title = request.form.get("title")
    priority = request.form.get("priority", "medium")
    category = request.form.get("category", "General")
    due_date = request.form.get("due_date") or None
    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO tasks (title, done, priority, category, due_date) VALUES (%s, %s, %s, %s, %s);",
                (title, False, priority, category, due_date))
    conn.commit(); cur.close(); conn.close()
    flash("Task added!", "success")
    return redirect(url_for("tasks"))

@app.route("/tasks/toggle/<int:task_id>", methods=["POST"])
def toggle_task(task_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE tasks SET done = NOT done WHERE id = %s;", (task_id,))
    conn.commit(); cur.close(); conn.close()
    return redirect(request.referrer or url_for("tasks"))

@app.route("/tasks/delete/<int:task_id>", methods=["POST"])
def delete_task(task_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM tasks WHERE id = %s;", (task_id,))
    conn.commit(); cur.close(); conn.close()
    flash("Task deleted.", "success")
    return redirect(request.referrer or url_for("tasks"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)