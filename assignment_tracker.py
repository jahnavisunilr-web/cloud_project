from flask import Flask, request, redirect, render_template_string
import sqlite3

app = Flask(__name__)

# ---------------- DATABASE ----------------

def create_database():
    conn = sqlite3.connect("assignments.db")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            subject TEXT NOT NULL,
            deadline TEXT NOT NULL,
            priority TEXT NOT NULL,
            status TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


create_database()


# ---------------- HTML ----------------

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Assignment Deadline Tracker</title>

    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f4f6f8;
            margin: 0;
        }

        header {
            background: #2c3e50;
            color: white;
            text-align: center;
            padding: 30px;
        }

        .container {
            width: 90%;
            max-width: 1000px;
            margin: 30px auto;
        }

        .cards {
            display: flex;
            gap: 20px;
            margin-bottom: 25px;
        }

        .card {
            background: white;
            padding: 20px;
            flex: 1;
            text-align: center;
            border-radius: 10px;
        }

        .card h2 {
            font-size: 30px;
        }

        .add {
            display: inline-block;
            background: #27ae60;
            color: white;
            padding: 12px 20px;
            text-decoration: none;
            border-radius: 5px;
            margin-bottom: 20px;
        }

        table {
            width: 100%;
            background: white;
            border-collapse: collapse;
        }

        th {
            background: #34495e;
            color: white;
        }

        th, td {
            padding: 14px;
            border-bottom: 1px solid #ddd;
        }

        .complete {
            background: #3498db;
            color: white;
            padding: 6px 10px;
            text-decoration: none;
            border-radius: 4px;
        }

        .delete {
            background: #e74c3c;
            color: white;
            padding: 6px 10px;
            text-decoration: none;
            border-radius: 4px;
        }

        .pending {
            color: orange;
            font-weight: bold;
        }

        .completed {
            color: green;
            font-weight: bold;
        }

        form {
            background: white;
            padding: 30px;
            max-width: 500px;
            margin: 30px auto;
            border-radius: 10px;
        }

        input, select {
            width: 100%;
            padding: 12px;
            margin: 8px 0 15px;
            box-sizing: border-box;
        }

        button {
            width: 100%;
            padding: 12px;
            background: #27ae60;
            color: white;
            border: none;
            border-radius: 5px;
            font-size: 16px;
        }
    </style>
</head>

<body>

<header>
    <h1>Assignment Deadline Tracker</h1>
    <p>Manage your university assignments easily</p>
</header>

<div class="container">

    {% if page == "home" %}

    <div class="cards">

        <div class="card">
            <h3>Total Assignments</h3>
            <h2>{{ total }}</h2>
        </div>

        <div class="card">
            <h3>Pending</h3>
            <h2>{{ pending }}</h2>
        </div>

        <div class="card">
            <h3>Completed</h3>
            <h2>{{ completed }}</h2>
        </div>

    </div>

    <a href="/add" class="add">+ Add Assignment</a>

    <h2>My Assignments</h2>

    {% if assignments %}

    <table>

        <tr>
            <th>Assignment</th>
            <th>Subject</th>
            <th>Deadline</th>
            <th>Priority</th>
            <th>Status</th>
            <th>Action</th>
        </tr>

        {% for a in assignments %}

        <tr>

            <td>{{ a[1] }}</td>
            <td>{{ a[2] }}</td>
            <td>{{ a[3] }}</td>
            <td>{{ a[4] }}</td>

            <td>
                {% if a[5] == "Completed" %}
                    <span class="completed">Completed</span>
                {% else %}
                    <span class="pending">Pending</span>
                {% endif %}
            </td>

            <td>

                {% if a[5] == "Pending" %}
                <a href="/complete/{{ a[0] }}" class="complete">
                    Complete
                </a>
                {% endif %}

                <a href="/delete/{{ a[0] }}" class="delete">
                    Delete
                </a>

            </td>

        </tr>

        {% endfor %}

    </table>

    {% else %}

    <p>No assignments added yet.</p>

    {% endif %}

    {% else %}

    <form method="POST" action="/add">

        <h2>Add Assignment</h2>

        <label>Assignment Name</label>
        <input type="text" name="title"
               placeholder="Example: Python Project"
               required>

        <label>Subject</label>
        <input type="text" name="subject"
               placeholder="Example: Python"
               required>

        <label>Deadline</label>
        <input type="date" name="deadline" required>

        <label>Priority</label>

        <select name="priority">
            <option>High</option>
            <option selected>Medium</option>
            <option>Low</option>
        </select>

        <button type="submit">
            Add Assignment
        </button>

        <br><br>

        <a href="/">← Back to Dashboard</a>

    </form>

    {% endif %}

</div>

</body>
</html>
"""


# ---------------- HOME PAGE ----------------

@app.route("/")
def home():

    conn = sqlite3.connect("assignments.db")

    assignments = conn.execute(
        "SELECT * FROM assignments ORDER BY deadline"
    ).fetchall()

    total = len(assignments)

    completed = conn.execute(
        "SELECT COUNT(*) FROM assignments WHERE status='Completed'"
    ).fetchone()[0]

    pending = conn.execute(
        "SELECT COUNT(*) FROM assignments WHERE status='Pending'"
    ).fetchone()[0]

    conn.close()

    return render_template_string(
        HTML,
        page="home",
        assignments=assignments,
        total=total,
        completed=completed,
        pending=pending
    )


# ---------------- ADD ASSIGNMENT ----------------

@app.route("/add", methods=["GET", "POST"])
def add_assignment():

    if request.method == "POST":

        title = request.form["title"]
        subject = request.form["subject"]
        deadline = request.form["deadline"]
        priority = request.form["priority"]

        conn = sqlite3.connect("assignments.db")

        conn.execute("""
            INSERT INTO assignments
            (title, subject, deadline, priority, status)
            VALUES (?, ?, ?, ?, ?)
        """, (
            title,
            subject,
            deadline,
            priority,
            "Pending"
        ))

        conn.commit()
        conn.close()

        return redirect("/")

    return render_template_string(
        HTML,
        page="add"
    )


# ---------------- COMPLETE ----------------

@app.route("/complete/<int:id>")
def complete(id):

    conn = sqlite3.connect("assignments.db")

    conn.execute(
        "UPDATE assignments SET status='Completed' WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/")


# ---------------- DELETE ----------------

@app.route("/delete/<int:id>")
def delete(id):

    conn = sqlite3.connect("assignments.db")

    conn.execute(
        "DELETE FROM assignments WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/")


# ---------------- RUN ----------------

if __name__ == "__main__":
    app.run(debug=True)
