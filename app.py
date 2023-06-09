"""App entry point."""
import os
from flask import Flask
from flask import request
from flask import url_for
from flask import redirect, session
from flask import render_template as rt
from flask import flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

import pandas as pd
import plotly.express as px
from flask import render_template_string

from myapp import create_app

# Create Flask app
app = create_app()
app.secret_key = "ABCabc123"
app.debug = True


# --- Start of Database ---

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.abspath(
    "myapp/database/database.db"
)
# Prevent sql-inject, not practical sql injection, sqlchemy makes the code ORM, safe execution
db = SQLAlchemy(app)

admin_list = ["admin@gmail.com", "ymj@gmail.com"]

class Users(db.Model):
    """Create users table"""
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

class Products(db.Model):
    """Create products table"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    text = db.Column(db.Text)
    image = db.Column(db.String(255))

    def __init__(self, title, text, image=None):
        """Initialization method"""
        self.title = title
        self.text = text
        self.image = image

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
    products = Products.query.all()
    products = list(reversed(products))
    user = None
    if "userid" in session:
        user = Users.query.filter_by(id=session["userid"]).first()

    # Search for the title and text keywords of the predicte_category
    if request.method == "POST":
        search_list = []
        keyword = request.form["keyword"]
        if keyword is not None:
            for products in products:
                if keyword in products.title or keyword in products.text:
                    products.title = replace_html_tag(products.title, keyword)
                    products.text = replace_html_tag(products.text, keyword)
                    
                    search_list.append(products)

        return rt(
            "home.html",
            listing=PageResult(search_list, pagenum, 10),
            user=user,
            keyword=keyword,
        )
    
    return rt("home.html", listing=PageResult(products, pagenum), user=user)

# --- End of Home ---


# --- Start of login, register and logout ---

@app.route("/login", methods=["POST"])
def login():
    email = request.form.get("email")
    password = request.form.get("password")
    # Go to the database to query the email and password
    data = Users.query.filter_by(username=email, password=password).first()
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
    data = Users.query.filter_by(username=email).first()
    # If the email is already in the database
    if data is not None:
        flash("This email has already been registered, please try another one!")
        return redirect(url_for("home", pagenum=1))
    print("Register", email, pw1)
    new_user = Users(username=email, password=pw1)
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for("home", pagenum=1))


@app.route("/logout")
def logout():
    session["logged_in"] = False
    return redirect(url_for("home", pagenum=1))

# --- End of login, register and logout ---

# --- Start of profile ---

@app.route("/profile", methods=["GET"])
def query_profile():
    """Query profile details"""
    id = session["userid"]
    if request.method == "GET":
        # Go to the database to query the profile details based on ID
        user = Users.query.filter_by(id=id).first_or_404()
        # Render "profile" page
        return rt("profile.html", user=user)

@app.route("/profile/update/<id>", methods=["GET", "POST"])
def update_profile(id):
    """Update Profile details"""
    if request.method == "GET":
        # Go to the database to query the profile details based on ID
        user = Users.query.filter_by(id=id).first_or_404()
        # Render the HTML template of the "update_profile" page
        return rt("update_profile.html", user=user)
    else:
        # Get the requested profile details
        nickname = request.form["nickname"]
        occupation = request.form["occupation"]
        educational_background = request.form["educational_background"]
        password = request.form["password"]

        # Update profile details
        user = Users.query.filter_by(id=id).update(
            {
                "nickname": nickname,
                "occupation": occupation,
                "educational_background": educational_background,
                "password": password,
            }
        )
        # Must be submitted to take effect
        db.session.commit()
        # After the update is complete, redirect to the "profile" page
        return redirect("/profile")

# --- End of profile ---


# --- Start of predict_category products (CRUD) ---

@app.route("/products", methods=["GET"])
def manage_products():
    """Query the list of predict categories"""
    products = Products.query.all()

    # Render the target file of the "manage_products" page, and pass in the products parameter
    return rt("manage_products.html", products=products)

@app.route("/products/create", methods=["GET", "POST"])
def create_products():
    """Create predict category"""
    if request.method == "GET":
        # If it is a GET request, render the creation page
        return rt("create_products.html")
    else:
        # Get request data from the form request body
        title = request.form["title"]
        text = request.form["text"]
        image = request.files["image"]

        if '.' in image.filename and image.filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']:
            # save the image file
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            # Create a predict category object, title and text and image
            products = Products(title=title, text=text, image=filename)
            db.session.add(products)
            # Must be submitted to take effect
            db.session.commit()
            # After the creation is complete, redirect to the "manage_products" page
            return redirect("/products")
        
        return redirect(request.url)


@app.route("/products/<id>", methods=["GET", "DELETE"])
def query_products(id):
    """Query Predict_Category details, delete Predict_Category"""
    if request.method == "GET":
        # Go to the database to query predict category details based on ID
        products = Products.query.filter_by(id=id).first_or_404()
        # Render "query_products" page
        return rt("query_products.html", products=products)
    else:
        # Delete the predict_category
        products = Products.query.filter_by(id=id).delete()
        # Must be submitted to take effect
        db.session.commit()
        # Return 204 normal response, otherwise the page ajax will report an error
        return "", 204

@app.route("/products/update/<id>", methods=["GET", "POST"])
def update_products(id):
    """Update Predict Category"""
    if request.method == "GET":
        # Go to the database to query predict category details based on ID
        products = Products.query.filter_by(id=id).first_or_404()
        # Render the HTML template of the "update_products" page
        return rt("update_products.html", products=products)
    else:
        # Get the title and text of the requested predict category
        title = request.form["title"]
        text = request.form["text"]
        image = request.files["image"]
        
        if '.' in image.filename and image.filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']:
            # save the image file
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            # Update the title and text and image of the predict category
            products = Products.query.filter_by(id=id).update({"title": title, "text": text, "image": filename})
        else:
            # Update the title and text only if the image is not valid or not provided
            products = Products.query.filter_by(id=id).update({"title": title, "text": text})
            
        # Must be submitted to take effect
        db.session.commit()
        # After the update is complete, redirect to the "query_products" page
        return redirect("/products/{id}".format(id=id))

# --- End of predict category blog (CRUD) ---


# --- Start of visualization of prediction results ---

@app.route("/plot_demand/<string:material>")
def plot_demand(material):
    material = material.lower()
    if material == "aggregate":
        file_path = "data/Aggregate/predictions_2023.csv"
        title = "Demand Prediction for 2023 (Aggregate)"
    elif material == "concrete":
        file_path = "data/Concrete/predictions_2023.csv"
        title = "Demand Prediction for 2023 (Concrete)"
    else:
        return "Invalid material. Please choose 'Aggregate' or 'Concrete'."

    # Read forecast data from CSV file
    predictions_2023_df = pd.read_csv(file_path)

    # Create Interactive Line Charts with Plotly
    fig = px.line(predictions_2023_df, x='timestamp', y='prediction', title=title)

    # Convert graphics to HTML
    plot_html = fig.to_html(full_html=False)

    return render_template_string(f"""
    <!DOCTYPE html>
    <html>
        <head>
            <title>{title}</title>
        </head>
        <body>
            {plot_html}
        </body>
    </html>
    """)

# --- End of visualization of prediction results ---


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

        app.run(host="localhost", port=5000, threaded=False)