from flask import Flask, render_template, request, session
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_migrate import Migrate
import sys
from flask_mail import Mail
import json

with open('config.json', 'r') as c:
    params = json.load(c)['parameters']
local_server = True

app = Flask(__name__)
app.secret_key = 'key'
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT='465',
    MAIL_USE_SSL=True,
    MAIL_USERNAME=params['gmail_id'],
    MAIL_PASSWORD=params['gmail_password'],

)
mail = Mail(app)
if local_server:
    app.config["SQLALCHEMY_DATABASE_URI"] = params['local_uri']
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = params['production_server']

db = SQLAlchemy(app)

# login_manager = LoginManager()
# login_manager.init_app(app)

class Contact(db.Model):
    """
    name message email time sno """

    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    message = db.Column(db.String(120), nullable=False)
    time = db.Column(db.String(12), nullable=True)
    email = db.Column(db.String(20), nullable=False)
    # print(name, file=sys.stderr)


class Posts(db.Model):
    """Fetching posts through database"""

    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    content = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    slug = db.Column(db.String(25), nullable=False)
    img_file = db.Column(db.String(25), nullable=False)
    tagline = db.Column(db.String(25), nullable=True)


@app.route('/home')
def homepage():
    # return 'This is homepage of Tanish !'
    posts = Posts.query.filter_by().all()[0:5]
    return render_template("index.html", params=params, posts=posts)


@app.route('/')
def homepage2():
    # return 'This is homepage of Tanish !'
    posts = Posts.query.filter_by().all()[0:5]
    return render_template("index.html", params=params, posts=posts)


@app.route('/about')
def about():

    return render_template("about.html", params=params)


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if (request.method == 'POST'):
        # add entry to the database
        username = request.form.get('name')
        message = request.form.get('message')
        email = request.form.get('email')

        entry = Contact(name=username, message=message,
                        time=datetime.now(), email=email)
        db.session.add(entry)
        db.session.commit()
        mail.send_message(
            f"New message from {username}",
            sender=email, recipients=[params['gmail_id']], body=f"{message}\n{username}\n{email}\n{datetime.now()}\n")

    return render_template("contact.html", params=params)


@app.route('/post/<string:post_slug>', methods=['GET'])
def post(post_slug):
    posts = Posts.query.filter_by(slug=post_slug).first()
    return render_template("post.html", params=params, post=posts)


# @login_manager.user_loader
# def load_user(user_id):
#     """Login manager"""
#     return User.get(user_id)


# @app.route('/dashboard', methods=['GET', 'POST'])
# def dashboard():
#     if ('user' in session and session['user'] == params["admin_username"]):
#         return render_template("dashboard.html", params=params)
#     if request.method == "POST":
#         # redirect to the admin panel
#         uname = request.form.get('username')
#         password = request.form.get('pass')
#         if (uname == params["admin_username"] and password == params["admin_password"]):
#             # set up session variable
#             session['user'] = uname
#             return render_template("dashboard.html", params=params)
#     return render_template("login.html", params=params)


if __name__ == '__main__':

    app.run(debug=True)
