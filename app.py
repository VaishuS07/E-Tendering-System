from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = "etendering-secret-key"

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Server@123",
    "database": "etendering"
}

def db():
    return mysql.connector.connect(**DB_CONFIG)
def login_required():
    if "user_id" not in session:
        return False
    return True

@app.route("/")
def home():
    conn = db()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT COUNT(*) AS count FROM agency")
    agencies = cur.fetchone()["count"]

    cur.execute("SELECT COUNT(*) AS count FROM bidder")
    bidders = cur.fetchone()["count"]

    cur.execute("SELECT COUNT(*) AS count FROM tender")
    tenders = cur.fetchone()["count"]

    cur.execute("SELECT COUNT(*) AS count FROM bid")
    bids = cur.fetchone()["count"]

    cur.execute("""
        SELECT tender_id, tender_title, deadline
        FROM tender
        WHERE deadline >= CURDATE()
        AND deadline <= DATE_ADD(CURDATE(), INTERVAL 7 DAY)
        ORDER BY deadline
    """)

    deadline_alerts = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        "index.html",
        agencies=agencies,
        bidders=bidders,
        tenders=tenders,
        bids=bids,
        deadline_alerts=deadline_alerts
    )
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = db()
        cur = conn.cursor(dictionary=True)

        cur.execute(
            "SELECT * FROM users WHERE username=%s AND password=%s",
            (username, password)
        )

        user = cur.fetchone()

        cur.close()
        conn.close()

        if user:
            session["user_id"] = user["user_id"]
            session["username"] = user["username"]
            session["role"] = user["role"]
            return redirect(url_for("home"))

        else:
            flash("Invalid username or password.", "danger")
    return render_template("login.html")
@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))

@app.route("/agencies")
def agencies():
    if not login_required():
        return redirect(url_for("login"))
    conn = db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM agency ORDER BY agency_id")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("agencies.html", rows=rows)

@app.route("/bidders")
def bidders():
    if not login_required():
        return redirect(url_for("login"))

    conn = db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM bidder ORDER BY bidder_id")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("bidders.html", rows=rows)

@app.route("/tenders")
def tenders():
    if not login_required():
        return redirect(url_for("login"))
    search = request.args.get("search", "")
    conn = db()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT t.*, a.agency_name
        FROM tender t
        LEFT JOIN agency a ON t.agency_id = a.agency_id
        ORDER BY t.tender_id
    """)

    rows = cur.fetchall()

    cur.execute("SELECT * FROM agency ORDER BY agency_name")
    agencies = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        "tenders.html",
        rows=rows,
        agencies=agencies
    )

@app.route("/agency/add", methods=["POST"])
def add_agency():
    conn = db()
    cur = conn.cursor()

    try:
        cur.execute("""
            INSERT INTO agency
            (agency_id, agency_name, email, phone, address)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            request.form["agency_id"],
            request.form["agency_name"],
            request.form["email"],
            request.form["phone"],
            request.form["address"]
        ))

        conn.commit()
        flash("Agency added successfully.", "success")

    except Error as e:
        conn.rollback()
        flash(str(e), "danger")

    finally:
        cur.close()
        conn.close()

    return redirect(url_for("agencies"))

@app.route("/agency/delete/<int:agency_id>", methods=["POST"])
def delete_agency(agency_id):
    conn = db()
    cur = conn.cursor()

    try:
        cur.execute(
            "DELETE FROM agency WHERE agency_id=%s",
            (agency_id,)
        )

        conn.commit()
        flash("Agency deleted successfully.", "success")

    except Error as e:
        conn.rollback()
        flash(str(e), "danger")

    finally:
        cur.close()
        conn.close()

    return redirect(url_for("agencies"))



@app.route("/agency/edit/<int:agency_id>", methods=["GET", "POST"])
def edit_agency(agency_id):
    conn = db()
    cur = conn.cursor(dictionary=True)

    if request.method == "POST":
        cur.execute("""
            UPDATE agency
            SET agency_name=%s,
                email=%s,
                phone=%s,
                address=%s
            WHERE agency_id=%s
        """, (
            request.form["agency_name"],
            request.form["email"],
            request.form["phone"],
            request.form["address"],
            agency_id
        ))

        conn.commit()
        cur.close()
        conn.close()

        flash("Agency updated successfully.", "success")
        return redirect(url_for("agencies"))

    cur.execute(
        "SELECT * FROM agency WHERE agency_id=%s",
        (agency_id,)
    )

    agency = cur.fetchone()

    cur.close()
    conn.close()

    return render_template(
        "edit_agency.html",
        agency=agency
    )
@app.route("/bidder/add", methods=["POST"])
def add_bidder():
    conn = db()
    cur = conn.cursor()

    try:
        cur.execute("""
            INSERT INTO bidder
            (bidder_name, email, phone, company_name, address)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            request.form["bidder_name"],
            request.form["email"],
            request.form["phone"],
            request.form["company_name"],
            request.form["address"]
        ))

        conn.commit()
        flash("Bidder added successfully.", "success")

    except Error as e:
        conn.rollback()
        flash(str(e), "danger")

    finally:
        cur.close()
        conn.close()

    return redirect(url_for("bidders"))

@app.route("/bidder/edit/<int:bidder_id>", methods=["GET", "POST"])
def edit_bidder(bidder_id):
    conn = db()
    cur = conn.cursor(dictionary=True)

    if request.method == "POST":
        cur.execute("""
            UPDATE bidder
            SET bidder_name=%s,
                email=%s,
                phone=%s,
                company_name=%s,
                address=%s
            WHERE bidder_id=%s
        """, (
            request.form["bidder_name"],
            request.form["email"],
            request.form["phone"],
            request.form["company_name"],
            request.form["address"],
            bidder_id
        ))

        conn.commit()
        cur.close()
        conn.close()

        flash("Bidder updated successfully.", "success")
        return redirect(url_for("bidders"))

    cur.execute(
        "SELECT * FROM bidder WHERE bidder_id=%s",
        (bidder_id,)
    )

    bidder = cur.fetchone()

    cur.close()
    conn.close()

    return render_template(
        "edit_bidder.html",
        bidder=bidder
    )


@app.route("/bidder/delete/<int:bidder_id>", methods=["POST"])
def delete_bidder(bidder_id):
    conn = db()
    cur = conn.cursor()

    try:
        cur.execute(
            "DELETE FROM bidder WHERE bidder_id=%s",
            (bidder_id,)
        )

        conn.commit()
        flash("Bidder deleted successfully.", "success")

    except Error as e:
        conn.rollback()
        flash(str(e), "danger")

    finally:
        cur.close()
        conn.close()

    return redirect(url_for("bidders"))


@app.route("/tender/add", methods=["POST"])
def add_tender():
    conn = db()
    cur = conn.cursor()

    try:
        cur.execute("""
            INSERT INTO tender
            (tender_title, description, agency_id,
             tender_amount, deadline, status)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            request.form["tender_title"],
            request.form["description"],
            request.form["agency_id"],
            request.form["tender_amount"],
            request.form["deadline"],
            request.form["status"]
        ))

        conn.commit()
        flash("Tender added successfully.", "success")

    except Error as e:
        conn.rollback()
        flash(str(e), "danger")

    finally:
        cur.close()
        conn.close()

    return redirect(url_for("tenders"))

@app.route("/tender/edit/<int:tender_id>", methods=["GET", "POST"])
def edit_tender(tender_id):
    conn = db()
    cur = conn.cursor(dictionary=True)

    if request.method == "POST":
        cur.execute("""
            UPDATE tender
            SET tender_title=%s,
                description=%s,
                agency_id=%s,
                tender_amount=%s,
                deadline=%s,
                status=%s
            WHERE tender_id=%s
        """, (
            request.form["tender_title"],
            request.form["description"],
            request.form["agency_id"],
            request.form["tender_amount"],
            request.form["deadline"],
            request.form["status"],
            tender_id
        ))

        conn.commit()
        cur.close()
        conn.close()

        flash("Tender updated successfully.", "success")
        return redirect(url_for("tenders"))

    cur.execute(
        "SELECT * FROM tender WHERE tender_id=%s",
        (tender_id,)
    )
    tender = cur.fetchone()

    cur.execute("SELECT * FROM agency ORDER BY agency_name")
    agencies = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        "edit_tender.html",
        tender=tender,
        agencies=agencies
    )



@app.route("/tender/delete/<int:tender_id>", methods=["POST"])
def delete_tender(tender_id):
    conn = db()
    cur = conn.cursor()

    try:
        cur.execute(
            "DELETE FROM tender WHERE tender_id=%s",
            (tender_id,)
        )

        conn.commit()
        flash("Tender deleted successfully.", "success")

    except Error as e:
        conn.rollback()
        flash(str(e), "danger")

    finally:
        cur.close()
        conn.close()

    return redirect(url_for("tenders"))


@app.route("/bids")
def bids():
    if not login_required():
        return redirect(url_for("login"))

    conn = db()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT b.*, 
               t.tender_title,
               bd.bidder_name,
               bd.company_name
        FROM bid b
        JOIN tender t ON b.tender_id = t.tender_id
        JOIN bidder bd ON b.bidder_id = bd.bidder_id
        ORDER BY b.bid_id DESC
    """)

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("bids.html", rows=rows)


@app.route("/bid/<int:bid_id>/status", methods=["POST"])
def update_bid_status(bid_id):

    conn = db()
    cur = conn.cursor()

    try:

        cur.execute("""
            UPDATE bid
            SET status=%s
            WHERE bid_id=%s
        """, (
            request.form["status"],
            bid_id
        ))

        conn.commit()

        flash("Bid status updated successfully.", "success")

    except Error as e:

        conn.rollback()
        flash(str(e), "danger")

    finally:

        cur.close()
        conn.close()

    return redirect(url_for("bids"))

if __name__ == "__main__":
    app.run(debug=True)