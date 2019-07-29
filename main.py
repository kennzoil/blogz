from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy
from functions import *
from os import urandom

app = Flask(__name__)
app.config["DEBUG"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://blogz:123@localhost:8889/blogz"
app.config["SQLALCHEMY_ECHO"] = True
app.secret_key = urandom(16)
db = SQLAlchemy(app)


class BlogPost(db.Model):

    blogpost_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable=False)

    def __init__(self, title, content, user_id):
        self.title = title
        self.content = content
        self.user = user_id

class User(db.Model):

    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(22), nullable=False)
    password = db.Column(db.String(120), nullable=False)
    blogs = db.relationship("BlogPost", backref="user", lazy=True)

    def __init__(self, username, password):

        self.username = username
        self.password = password


@app.before_request
def require_login():
    allowed_routes = ["login", "signup", "blog", "index"]
    if request.endpoint not in allowed_routes and "username" not in session:
        return redirect("/login")

@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]
        passconfirm = request.form["pass_confirm"]

        errors = {
            "username": "",
            "password": "",
            "pass_confirm": "",
        }

        if valid_username(username) == False:
            errors["username"] = "Please enter a valid username, between 3 and 20 characters, with no spaces."
        if valid_password(password) == False:
            errors["password"] = "Don't forget your password!"
        if passwords_match(password, passconfirm) == False:
            errors["pass_confirm"] = "Make sure your passwords match."

        if list(errors.values()) == ["", "", ""]:
            existing_user = User.query.filter_by(username = username).first()
            if not existing_user:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session["username"] = username
                return redirect(
                    "/newpost"
                )
            else:
                return render_template(
                    "signup.html",
                    title = "Sign Up",
                    username_error = "User with this username already exists."
                )
        else:
            return render_template(
                "signup.html",
                title = "Create an account",
                username_error = errors["username"],
                password_error = errors["password"],
                passconfirm_error = errors["pass_confirm"],
                username = username
            )
    elif request.method == "GET":
        return render_template(
            "signup.html",
            title = "Create an account"
        )

@app.route("/login", methods=["GET", "POST"])
def login():

    # This block is for GET requests, when the login page is loaded normally.
    if request.method == "GET":
        return render_template(
            "login.html",
            title = "Log In"
        )

    # This block is for POST requests, when the 'Log In' button is clicked.
    elif request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # If either field is left blank, this happens.
        if not (username and password):
            username_error = ""
            password_error = ""
            if not username:
                username_error = "Enter a username."
            if not password:
                password_error = "Enter a password."

            return render_template(
                "login.html",
                title = "Log In",
                username = username,
                username_error = username_error,
                password_error = password_error
            )

        # Get the user from the database
        user = User.query.filter_by(username = username).first()

        if not user:
            return render_template(
                "login.html",
                title = "Log In",
                username_error = "Impossible. Perhaps the archives are incomplete."
            )
        
        if user.password != password:
            return render_template(
                "login.html",
                title = "Log In",
                password_error = "That's the wrong password.",
                username = username
            )

        session["username"] = username
        return redirect(
            "/newpost"
        )

@app.route("/")
def index():

    if request.method == "GET":

        users = User.query.all()

        return render_template(
            "index.html",
            users = users
        )

@app.route("/blog")
def blog():

    if request.args.get("id"):

        blog_id = int(request.args.get("id"))
        indiv_blog = BlogPost.query.get(blog_id)
        post_title = indiv_blog.title
        post_content = indiv_blog.content
        post_user = indiv_blog.user.username
        post_user_id = indiv_blog.user.user_id

        return render_template(
            "blog_post.html",
            title=post_title,
            post_title=post_title,
            post_content=post_content,
            post_user=post_user,
            post_user_id=post_user_id
        )

    elif request.args.get("user"):

        user_id = int(request.args.get("user"))
        indiv_user = User.query.get(user_id)
        blog_posts = indiv_user.blogs

        return render_template(
            "singleUser.html",
            title = "something",
            blog_posts = blog_posts,
            indiv_user = indiv_user
        )

    else:
        posts = BlogPost.query.all()

        return render_template(
            "blog.html",
            title = "My Blog Posts",
            posts = posts
        )

@app.route("/newpost", methods=["POST", "GET"])
def newpost():

    if request.method == "POST":

        title = request.form["title"]
        content = request.form["content"]
        user_id = User.query.filter_by(username=session["username"]).first()
        # TODO - fix this

        if title and content:
            post = BlogPost(title, content, user_id)
            db.session.add(post)
            db.session.commit()
            blog_id = post.blogpost_id

            return redirect(
                "/blog?id=" + str(blog_id)
            )

        else:
            re_title = ""
            re_content = ""
            if (not title) and content:
                re_content = content
                error_message = """
                You moron. You absolute dunce.\n
                How could you possibly write an entire blog post and forget to put in a title?\n
                My geriatric great-grandfather could do that without a second thought,\n
                and he needs a nurse's assistance to go to the bathroom.\n
                Write your title and submit it again,\n
                and try not to screw it up this time.
                """
            elif title and (not content):
                re_title = title
                error_message = """
                You wrote a title and completely skipped over the content section.\n
                What a stupid mistake. You complete imbecile. You monstrous cretin.\n
                You should be ashamed of yourself.\n
                Do it again, you ignoramous.\n
                Try not to screw up, will you?
                """
            else:
                error_message = "You're getting a little ahead of yourself there, buddy."

            return render_template(
                "newpost.html",
                title="Write a new post",
                error_message=error_message,
                re_title=re_title,
                re_content=re_content
            )

    elif request.method == "GET":

        return render_template(
            "newpost.html",
            title="Write a new post"
        )

@app.route("/logout")
def logout():
   del session["username"]
   return redirect("/blog")


if __name__ == "__main__":
    app.run()