"""App entry point."""
import os
from flask import Flask
from flask import request
from flask import url_for
from flask import redirect, session
from flask import render_template as rt
from flask_sqlalchemy import SQLAlchemy

from flask_cors import CORS
from flask import flash
from myapp import create_app

# Create Flask app
app = create_app()
app.secret_key = "ABCabc123"
app.debug = True



CORS(app)

# --- Start of Database ---

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.abspath(
    "myapp/database/database.db"
)
# Defense point 1: prevent sql-inject, not practical sql injection, sqlchemy makes the code ORM, safe execution
db = SQLAlchemy(app)

admin_list = ["admin@gmail.com", "ymj@gmail.com"]

class User(db.Model):
    """Create user table"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    nickname = db.Column(db.String(80))
    occupation = db.Column(db.String(80))
    educational_background = db.Column(db.String(80))
    password = db.Column(db.String(80))

    def __init__(self, username, password):
        """Initialization method"""
        self.username = username
        self.password = password


class Blog(db.Model):
    """Create blog table"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    text = db.Column(db.Text)

    def __init__(self, title, text):
        """Initialization method"""
        self.title = title
        self.text = text

# --- End of Database ---


# --- Start of Home ---
#Search function on the page: search for the entered word or text, and the searched content will be displayed in red font
def replace_html_tag(text, word):
    new_word = '<font color="red">' + word + "</font>"
    len_w = len(word)
    len_t = len(text)
    for i in range(len_t - len_w, -1, -1):
        if text[i : i + len_w] == word:
            text = text[:i] + new_word + text[i + len_w :]
    return text


class PageResult:
    def __init__(self, data, page=1, number=4):
        self.__dict__ = dict(zip(["data", "page", "number"], [data, page, number]))
        self.full_listing = [
            self.data[i : i + number] for i in range(0, len(self.data), number)
        ]
        self.totalpage = len(data) // number

    def __iter__(self):
        if self.page - 1 < len(self.full_listing):
            for i in self.full_listing[self.page - 1]:
                yield i
        else:
            return None

    def __repr__(self):  # used for page linking
        return "/home/{}".format(self.page + 1)  # view the next page

@app.route("/home/<int:pagenum>", methods=["GET"])
@app.route("/home", methods=["GET", "POST"])
def home(pagenum=1):
    blogs = Blog.query.all()
    blogs = list(reversed(blogs))
    user = None
    if "userid" in session:
        user = User.query.filter_by(id=session["userid"]).first()

    # Search for the title and text keywords of the predicte_category
    if request.method == "POST":
        search_list = []
        keyword = request.form["keyword"]
        if keyword is not None:
            for blog in blogs:
                if keyword in blog.title or keyword in blog.text:
                    blog.title = replace_html_tag(blog.title, keyword)
                    blog.text = replace_html_tag(blog.text, keyword)
                    
                    search_list.append(blog)

        return rt(
            "home.html",
            listing=PageResult(search_list, pagenum, 10),
            user=user,
            keyword=keyword,
        )
    
    return rt("home.html", listing=PageResult(blogs, pagenum), user=user)

# --- End of Home ---


# --- Start of login, register and logout ---

@app.route("/login", methods=["POST"])
def login():
    email = request.form.get("email")
    password = request.form.get("password")
    # Go to the database to query the email and password
    data = User.query.filter_by(username=email, password=password).first()
    if data is not None:
        session["logged_in"] = True
        if email in admin_list:
            session["isadmin"] = True
        session["userid"] = data.id
        return redirect(url_for("home", pagenum=1))
    else:
        return "Login failed, invalid email or wrong password!"


@app.route("/register", methods=["POST"])
def register():
    email = request.form.get("email")
    pw1 = request.form.get("password")
    pw2 = request.form.get("password2")
    if not pw1 == pw2:
        flash("The password is different from the confirmation password, please try again!")
        return redirect(url_for("home", pagenum=1))
    # Go to the database to query the email
    data = User.query.filter_by(username=email).first()
    # If the email is already in the database
    if data is not None:
        flash("This email has already been registered, please try another one!")
        return redirect(url_for("home", pagenum=1))
    print("Register", email, pw1)
    new_user = User(username=email, password=pw1)
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for("home", pagenum=1))


@app.route("/logout")
def logout():
    session["logged_in"] = False
    return redirect(url_for("home", pagenum=1))

# --- End of login, register and logout ---



if __name__ == "__main__":
    with app.app_context():
        db.create_all()

        app.run(host="localhost", port=5000, threaded=False)