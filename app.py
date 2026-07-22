from flask import Flask, render_template, request, redirect, session
import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024
app.secret_key = "my_local_news_secure_key_2026"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "manju"
UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def get_db():
    conn = sqlite3.connect("news.db")
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def home():
    conn = get_db()
    news = conn.execute(
        "SELECT * FROM news ORDER BY id DESC"
    ).fetchall()
    conn.close()

    return render_template("home.html", news=news)


@app.route("/news/<int:id>")
def news(id):
    conn = get_db()
    article = conn.execute(
        "SELECT * FROM news WHERE id=?",
        (id,)
    ).fetchone()
    conn.close()

    return render_template("news.html", article=article)


@app.route("/admin")
def admin():

    if "admin" not in session:
        return redirect("/login")

    return render_template("upload.html")


@app.route("/upload", methods=["POST"])
def upload():

    title = request.form["title"]
    location = request.form["location"]
    article = request.form["article"]

    image = request.files["image"]

    image_name = ""

    if image.filename:
        image_name = secure_filename(image.filename)
        image.save(
            os.path.join(
                app.config["UPLOAD_FOLDER"],
                image_name
            )
        )

    conn = get_db()

    conn.execute(
        """
        INSERT INTO news(title,article,image,location)
        VALUES(?,?,?,?)
        """,
        (title, article, image_name, location)
    )

    conn.commit()
    conn.close()

    return redirect("/")

@app.route("/login", methods=["GET","POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]


        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:

            session["admin"] = True

            return redirect("/dashboard")


        else:

            return "Invalid username or password"


    return render_template("login.html")

@app.route("/dashboard")
def dashboard():

    if "admin" not in session:
        return redirect("/login")


    conn = get_db()

    news = conn.execute(
        "SELECT * FROM news ORDER BY id DESC"
    ).fetchall()


    total = conn.execute(
        "SELECT COUNT(*) FROM news"
    ).fetchone()[0]


    conn.close()


    return render_template(
        "dashboard.html",
        news=news,
        total=total
    )

@app.route("/edit/<int:id>", methods=["GET","POST"])
def edit(id):

    if "admin" not in session:
        return redirect("/login")


    conn = get_db()


    if request.method == "POST":

        title = request.form["title"]
        location = request.form["location"]
        article = request.form["article"]
        category = request.form["category"]


        conn.execute(
        """
        UPDATE news

        SET title=?,
        location=?,
        article=?,
        category=?

        WHERE id=?

        """,
        (
        title,
        location,
        article,
        category,
        id
        )
        )


        conn.commit()

        conn.close()


        return redirect("/dashboard")


    news = conn.execute(
        "SELECT * FROM news WHERE id=?",
        (id,)
    ).fetchone()


    conn.close()


    return render_template(
        "edit.html",
        news=news
    )

@app.route("/delete/<int:id>")
def delete(id):

    if "admin" not in session:
        return redirect("/login")


    conn = get_db()


    conn.execute(
        "DELETE FROM news WHERE id=?",
        (id,)
    )


    conn.commit()

    conn.close()


    return redirect("/dashboard")
@app.route("/logout")
def logout():

    session.pop("admin", None)

    return redirect("/login")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)