from flask import Flask, render_template, request, redirect, session
import mysql.connector
import os

app = Flask(__name__)
app.secret_key = "railway_secret_key"

# ================= DATABASE CONNECTION =================
def connect_db():
    return mysql.connector.connect(
        host=os.environ.get("MYSQLHOST", "localhost"),
        user=os.environ.get("MYSQLUSER", "root"),
        password=os.environ.get("MYSQLPASSWORD", ""),
        database=os.environ.get("MYSQLDATABASE", ""),
        port=int(os.environ.get("MYSQLPORT", 3306))
    )

# ================= LOGIN =================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "admin123":
            session["role"] = "admin"
        else:
            session["role"] = "user"

        return redirect("/")

    return render_template("login.html")

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

    return render_template("index.html", records=records)

# ================= ADD TRAIN =================
@app.route("/add", methods=["GET", "POST"])
def add_train():
    if session.get("role") != "admin":
        return "Only Admin Can Add Trains"

    if request.method == "POST":
        train_no = request.form["train_no"]
        train_name = request.form["train_name"]
        source = request.form["source"]
        destination = request.form["destination"]
        total_seats = request.form["total_seats"]
        available_seats = request.form["available_seats"]

        con = connect_db()
        cur = con.cursor()

        cur.execute(
            "INSERT INTO trains VALUES (%s, %s, %s, %s, %s, %s)",
            (train_no, train_name, source, destination,
             total_seats, available_seats)
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
    cur.execute("DELETE FROM trains WHERE train_no = %s", (train_no,))
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
        train_name = request.form["train_name"]
        source = request.form["source"]
        destination = request.form["destination"]
        total_seats = request.form["total_seats"]
        available_seats = request.form["available_seats"]

        cur.execute("""
            UPDATE trains
            SET train_name=%s,
                source=%s,
                destination=%s,
                total_seats=%s,
                available_seats=%s
            WHERE train_no=%s
        """, (train_name, source, destination,
              total_seats, available_seats, train_no))

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
        name = request.form["name"]
        age = request.form["age"]
        gender = request.form["gender"]
        seats_booked = int(request.form["seats_booked"])

        cur.execute(
            "SELECT available_seats FROM trains WHERE train_no=%s",
            (train_no,)
        )
        result = cur.fetchone()

        if result and result[0] >= seats_booked:

            cur.execute(
                "INSERT INTO passengers (name, age, gender) VALUES (%s, %s, %s)",
                (name, age, gender)
            )
            passenger_id = cur.lastrowid

            cur.execute(
                "INSERT INTO bookings (passenger_id, train_no, seats_booked) VALUES (%s, %s, %s)",
                (passenger_id, train_no, seats_booked)
            )

            cur.execute(
                "UPDATE trains SET available_seats = available_seats - %s WHERE train_no=%s",
                (seats_booked, train_no)
            )

            con.commit()
            con.close()
            return redirect("/")

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