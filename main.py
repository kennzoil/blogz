from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["DEBUG"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://build-a-blog:123@localhost:8889/build-a-blog"
app.config["SQLALCHEMY_ECHO"] = True
db = SQLAlchemy(app)


class BlogPost(db.Model):

    blogpost_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    content = db.Column(db.Text)

    def __init__(self, title, content):
        self.title = title
        self.content = content


@app.route("/")
def index():

    return redirect(
        "/blog"
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
            title="Build A Blog",
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

        if title and content:
            post = BlogPost(title, content)
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
                error_message = "Write a title."
            elif title and (not content):
                re_title = title
                error_message = "Write some content."
            else:
                error_message = "Write something."

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