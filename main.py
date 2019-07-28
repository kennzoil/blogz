## TODO - add the following templates: signup.html, login.html, and index.html
## TODO - add a singleUser.html template that will be used to display only the blogs associated with a single given author.
## It will be used when we dynamically generate a page using a GET request with a user query parameter on the /blog route.
# TODO - add the following route handler functions: signup, login, and index
# TODO - have a logout function that handles a POST request to /logout and redirects the user to /blog after deleting the username from the session
## TODO - add a User class to make all this new functionality possible




from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
from functions import *

app = Flask(__name__)
app.config["DEBUG"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://blogz:123@localhost:8889/blogz"
app.config["SQLALCHEMY_ECHO"] = True
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


@app.route("/signup", methods=["POST"])
def signup():

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
        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session["username"] = username
            # TODO - fix this
            return redirect(
                "/newpost"
            )
    else:
        return render_template(
            "signup.html",
            title = "Sign Up",
            username_error = errors["username"],
            password_error = errors["password"],
            passconfirm_error = errors["pass_confirm"],
            username = username
        )

@app.route("/login")
def login():

    # User enters a username that is stored in the database with the correct password
    # and is redirected to the /newpost page with their username being stored in a session.

    # User enters a username that is stored in the database with an incorrect password
    # and is redirected to the /login page with a message that their password is incorrect.

    # User tries to login with a username that is not stored in the database
    # and is redirected to the /login page with a message that this username does not exist.

    # User does not have an account and clicks "Create Account"
    # and is directed to the /signup page.

    return render_template("login.html")

@app.route("/")
def index():

    return redirect(
        "/login"
    )

@app.route("/blog")
def blog():

    if request.args.get("id"):

        blog_id = int(request.args.get("id"))
        indiv_blog = BlogPost.query.get(blog_id)
        post_title = indiv_blog.title
        post_content = indiv_blog.content

        return render_template(
            "blog_post.html",
            title=post_title,
            post_title=post_title,
            post_content=post_content
        )

    else:
        blog_posts = BlogPost.query.all()

        return render_template(
            "blog.html",
            title="My Blog Posts",
            posts=blog_posts
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


if __name__ == "__main__":
    app.run()