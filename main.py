from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import cgi

app = Flask(__name__)
app.config['DEBUG'] = True      # displays runtime errors in the browser, too
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:password@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True

app.secret_key = 'secretkey'

db = SQLAlchemy(app)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(800))

    def __init__(self, title, body):
        self.title = title
        self.body = body

    def __repr__(self):
        return '<Blog %r>' % self.title


@app.route("/blog", methods=['POST', 'GET'])
def display_blog():
    #needs to receive info from new_post
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        new_post = Blog(title, body)
        db.session.add(new_post)
        db.session.commit()

        all_posts = Blog.query.all()
        last_post = all_posts[-1]
        if new_post == last_post:
            return redirect ('/post_display?id=' + str(new_post.id))
        else:
            return render_template("blog.html", all_posts=all_posts)
        


@app.route("/new_post", methods=['POST', 'GET'])
def create_new_post():
    #needs to send info to blog
    return render_template("new_post.html")

@app.route("/post_display", methods=['POST', 'GET'])
def display_post(): #NEED TO FIGURE OUT HOW TO RENDER TEMPLATE WITH CORRECT ID
    id = request.args.get('id')
    
    blog = Blog.query.get(id)
    blog_title = blog.title
    blog_body = blog.body

    return render_template("post_display.html", blog_title=blog_title, blog_body=blog_body)



app.run()