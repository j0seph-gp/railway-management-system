from flask import Flask, render_template, request, redirect, session
import mysql.connector
import os
from urllib.parse import urlparse

app = Flask(__name__)
app.secret_key = "railway_secret_key"

# ================= DATABASE CONNECTION =================
def connect_db():
    database_url = os.environ.get("DATABASE_URL")

    if database_url:
        url = urlparse(database_url)
        return mysql.connector.connect(
            host=url.hostname,
            user=url.username,
            password=url.password,
            database=url.path[1:],
            port=url.port
        )
    else:
        # Local fallback (for development)
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="your_local_password",
            database="railway_db"
        )

# ================= CREATE TABLES =================
def create_tables():
    con = connect_db()
    cur = con.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS trains (
            train_no INT PRIMARY KEY,
            train_name VARCHAR(100),
            source VARCHAR(100),
            destination VARCHAR(100),
            total_seats INT,
            available_seats INT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS passengers (
            passenger_id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100),
            age INT,
            gender VARCHAR(10)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            booking_id INT AUTO_INCREMENT PRIMARY KEY,
            passenger_id INT,
            train_no INT,
            seats_booked INT,
            FOREIGN KEY (passenger_id) REFERENCES passengers(passenger_id),
            FOREIGN KEY (train_no) REFERENCES trains(train_no)
        )
    """)

    con.commit()
    con.close()

create_tables()

# ================= LOGIN SELECTION PAGE =================
@app.route("/login")
def login():
    return render_template("login.html")

# ================= ADMIN LOGIN =================
@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "admin123":
            session["role"] = "admin"
            session["username"] = "Administrator"
            return redirect("/")
        else:
            return "Invalid Admin Credentials"

    return render_template("admin_login.html")

# ================= USER LOGIN =================
@app.route("/user_login", methods=["GET", "POST"])
def user_login():
    if request.method == "POST":
        username = request.form["username"]
        session["role"] = "user"
        session["username"] = username
        return redirect("/")

    return render_template("user_login.html")

# ================= LOGOUT =================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ================= HOME =================
@app.route("/")
def home():
    if "role" not in session:
        return redirect("/login")

    con = connect_db()
    cur = con.cursor()

    search = request.args.get("search")

    if search:
        cur.execute(
            "SELECT * FROM trains WHERE train_name LIKE %s",
            ("%" + search + "%",)
        )
    else:
        cur.execute("SELECT * FROM trains")

    records = cur.fetchall()
    con.close()

    return render_template("index.html", records=records, username=session.get("username"))

# ================= ADD TRAIN =================
@app.route("/add", methods=["GET", "POST"])
def add_train():
    if session.get("role") != "admin":
        return "Only Admin Can Add Trains"

    if request.method == "POST":
        con = connect_db()
        cur = con.cursor()

        cur.execute(
            "INSERT INTO trains VALUES (%s, %s, %s, %s, %s, %s)",
            (
                request.form["train_no"],
                request.form["train_name"],
                request.form["source"],
                request.form["destination"],
                request.form["total_seats"],
                request.form["available_seats"],
            )
        )

        con.commit()
        con.close()
        return redirect("/")

    return render_template("add_train.html")

# ================= DELETE TRAIN =================
@app.route("/delete/<int:train_no>")
def delete_train(train_no):
    if session.get("role") != "admin":
        return "Only Admin Can Delete"

    con = connect_db()
    cur = con.cursor()
    cur.execute("DELETE FROM trains WHERE train_no=%s", (train_no,))
    con.commit()
    con.close()
    return redirect("/")

# ================= EDIT TRAIN =================
@app.route("/edit/<int:train_no>", methods=["GET", "POST"])
def edit_train(train_no):
    if session.get("role") != "admin":
        return "Only Admin Can Edit"

    con = connect_db()
    cur = con.cursor()

    if request.method == "POST":
        cur.execute("""
            UPDATE trains
            SET train_name=%s,
                source=%s,
                destination=%s,
                total_seats=%s,
                available_seats=%s
            WHERE train_no=%s
        """, (
            request.form["train_name"],
            request.form["source"],
            request.form["destination"],
            request.form["total_seats"],
            request.form["available_seats"],
            train_no
        ))

        con.commit()
        con.close()
        return redirect("/")

    cur.execute("SELECT * FROM trains WHERE train_no=%s", (train_no,))
    train = cur.fetchone()
    con.close()
    return render_template("edit_train.html", train=train)

# ================= BOOK TICKET =================
@app.route("/book/<int:train_no>", methods=["GET", "POST"])
def book_ticket(train_no):
    if "role" not in session:
        return redirect("/login")

    con = connect_db()
    cur = con.cursor()

    if request.method == "POST":
        seats_booked = int(request.form["seats_booked"])

        cur.execute("SELECT available_seats FROM trains WHERE train_no=%s", (train_no,))
        result = cur.fetchone()

        if result and result[0] >= seats_booked:

            cur.execute(
                "INSERT INTO passengers (name, age, gender) VALUES (%s, %s, %s)",
                (
                    request.form["name"],
                    request.form["age"],
                    request.form["gender"]
                )
            )
            passenger_id = cur.lastrowid

            cur.execute(
                "INSERT INTO bookings (passenger_id, train_no, seats_booked) VALUES (%s, %s, %s)",
                (passenger_id, train_no, seats_booked)
            )
            booking_id = cur.lastrowid

            cur.execute(
                "UPDATE trains SET available_seats = available_seats - %s WHERE train_no=%s",
                (seats_booked, train_no)
            )

            con.commit()
            con.close()

            return render_template(
                "booking_success.html",
                booking_id=booking_id,
                train_no=train_no,
                seats=seats_booked
            )
        else:
            con.close()
            return "Not enough seats available!"

    con.close()
    return render_template("book_ticket.html", train_no=train_no)

# ================= VIEW BOOKINGS =================
@app.route("/bookings")
def view_bookings():
    if session.get("role") != "admin":
        return "Access Denied! Admins Only."

    con = connect_db()
    cur = con.cursor()

    cur.execute("""
        SELECT b.booking_id, p.name, p.age, p.gender,
               t.train_name, b.seats_booked
        FROM bookings b
        JOIN passengers p ON b.passenger_id = p.passenger_id
        JOIN trains t ON b.train_no = t.train_no
    """)

    records = cur.fetchall()
    con.close()

    return render_template("view_bookings.html", records=records)

# ================= MAIN =================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)