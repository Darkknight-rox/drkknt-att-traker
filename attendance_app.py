import json
import os
from flask import Flask, request, redirect, render_template_string, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "super-secret-key"

DATA_FILE = "attendance_data.json"
USER_FILE = "users.json"

subjects = [
    "Analog Communication Lab",
    "Data Structures and Algorithms Lab",
    "Digital Logic Design Lab",
    "Linear Integrated Circuits Lab",
    "Operating System Concepts Lab",
    "Analog Communication",
    "Data Structures and Algorithms",
    "Digital Logic Design (M2)",
    "Electro-Magnetic Field Theory",
    "Linear Integrated Circuits",
    "Operating System Concepts"
]

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f)

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        users = load_users()
        if username in users and check_password_hash(users[username], password):
            session["user"] = username
            return redirect("/dashboard")
        return "Invalid credentials"
    return render_template_string("""
    <!doctype html>
    <html lang="en"><head>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <title>Login</title></head>
    <body class="bg-light">
        <div class="container mt-5">
            <div class="card shadow-sm p-4">
                <h2 class="text-center mb-4">Harshith Attendance Tracker - Login</h2>
                <form method="post">
                    <div class="mb-3"><input class="form-control" name="username" placeholder="Username"></div>
                    <div class="mb-3"><input class="form-control" type="password" name="password" placeholder="Password"></div>
                    <div class="text-center"><button class="btn btn-primary" type="submit">Login</button></div>
                </form>
            </div>
        </div>
    </body></html>
    """)

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user" not in session:
        return redirect("/")
    data = load_data()
    selected_subject = request.form.get("subject") if request.method == "POST" else ""
    if request.method == "POST":
        subject = request.form["subject"]
        status = request.form["status"]
        if status != "noclass":
            data.setdefault(subject, []).append(status)
            save_data(data)
        return redirect(f"/dashboard?subject={subject}")

    selected_subject = request.args.get("subject", "")

    html = """
    <!doctype html>
    <html><head>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <title>Dashboard</title></head>
    <body class="bg-white">
        <div class="container mt-4">
            <h1 class="mb-4">Harshith Attendance Tracker</h1>
            <form method="post" class="row g-3 align-items-center mb-4">
                <div class="col-auto">
                    <label class="form-label">Subject:</label>
                    <select class="form-select" name="subject">
                        {% for subj in subjects %}
                        <option value="{{subj}}" {% if subj == selected_subject %}selected{% endif %}>{{subj}}</option>
                        {% endfor %}
                    </select>
                </div>
                <div class="col-auto">
                    <label class="form-label">Status:</label>
                    <select class="form-select" name="status">
                        <option value="present">Present</option>
                        <option value="absent">Absent</option>
                        <option value="off">Off Class</option>
                    </select>
                </div>
                <div class="col-auto">
                    <button class="btn btn-success mt-4" type="submit">Mark Attendance</button>
                </div>
            </form>
            <table class="table table-bordered table-striped">
                <thead class="table-dark"><tr><th>Subject</th><th>Held</th><th>Present</th><th>Absent</th><th>Off</th><th>%</th></tr></thead>
                <tbody>
                {% for subject, records in data.items() %}
                    {% set present = records|select('equalto', 'present')|list|length %}
                    {% set absent = records|select('equalto', 'absent')|list|length %}
                    {% set off = records|select('equalto', 'off')|list|length %}
                    {% set held = present + absent %}
                    {% set percent = (present / held * 100) if held > 0 else 0 %}
                    <tr>
                        <td>{{subject}}</td>
                        <td>{{held}}</td>
                        <td>{{present}}</td>
                        <td>{{absent}}</td>
                        <td>{{off}}</td>
                        <td>{{"%.2f"|format(percent)}}%</td>
                    </tr>
                {% endfor %}
                </tbody>
            </table>
            <div class="mt-3">
                <a href="/edit" class="btn btn-outline-primary btn-sm">Edit Attendance</a>
                <a href="/change-password" class="btn btn-outline-warning btn-sm">Change Password</a>
                <a href="/logout" class="btn btn-outline-danger btn-sm">Logout</a>
            </div>
        </div>
    </body></html>
    """
    return render_template_string(html, data=data, subjects=subjects, selected_subject=selected_subject)

@app.route("/edit", methods=["GET", "POST"])
def edit():
    if "user" not in session:
        return redirect("/")
    data = load_data()
    if request.method == "POST":
        subject = request.form["subject"]
        index = int(request.form["index"])
        if subject in data and 0 <= index < len(data[subject]):
            del data[subject][index]
            save_data(data)
        return redirect("/edit")

    html = """
    <!doctype html>
    <html><head>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <title>Edit Attendance</title></head>
    <body class="bg-light">
        <div class="container mt-4">
            <h2>Edit Attendance</h2>
            <form method="post" class="row g-3 mb-4">
                <div class="col-md-5">
                    <label>Subject:</label>
                    <select class="form-select" name="subject" onchange="this.form.submit()">
                        <option disabled selected>Select a subject</option>
                        {% for subj in data %}
                        <option value="{{subj}}">{{subj}}</option>
                        {% endfor %}
                    </select>
                </div>
            </form>
            {% if data %}
                {% for subject, records in data.items() %}
                    <h5>{{subject}}</h5>
                    <ul class="list-group mb-3">
                    {% for entry in records %}
                        <li class="list-group-item d-flex justify-content-between align-items-center">
                            {{ loop.index0 }} - {{entry}}
                            <form method="post" class="m-0">
                                <input type="hidden" name="subject" value="{{subject}}">
                                <input type="hidden" name="index" value="{{loop.index0}}">
                                <button class="btn btn-sm btn-danger">Delete</button>
                            </form>
                        </li>
                    {% endfor %}
                    </ul>
                {% endfor %}
            {% endif %}
            <a href="/dashboard" class="btn btn-secondary">Back to Dashboard</a>
        </div>
    </body></html>
    """
    return render_template_string(html, data=data)

@app.route("/change-password", methods=["GET", "POST"])
def change_password():
    if "user" not in session:
        return redirect("/")
    if request.method == "POST":
        current = request.form["current"]
        new = request.form["new"]
        users = load_users()
        if check_password_hash(users[session["user"]], current):
            users[session["user"]] = generate_password_hash(new)
            save_users(users)
            return redirect("/dashboard")
        return "Current password incorrect"
    return render_template_string("""
    <!doctype html>
    <html><head>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <title>Change Password</title></head>
    <body class="bg-light">
        <div class="container mt-5">
            <div class="card p-4 shadow">
                <h2 class="mb-3">Change Password</h2>
                <form method="post">
                    <div class="mb-3"><input class="form-control" type="password" name="current" placeholder="Current Password"></div>
                    <div class="mb-3"><input class="form-control" type="password" name="new" placeholder="New Password"></div>
                    <button class="btn btn-primary" type="submit">Change</button>
                    <a href="/dashboard" class="btn btn-secondary ms-2">Back</a>
                </form>
            </div>
        </div>
    </body></html>
    """)

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")

if __name__ == "__main__":
    if not os.path.exists(USER_FILE):
        users = {"admin": generate_password_hash("harshith123")}
        save_users(users)
    app.run(debug=True)






