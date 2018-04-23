from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import cgi
import os

app = Flask(__name__)
app.config['DEBUG'] = True      # displays runtime errors in the browser, too
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:password@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True

app.secret_key = 'secretkey'

db = SQLAlchemy(app)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(800))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

    def __repr__(self):
        return '<Blog %r>' % self.title

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(120), unique = True)
    password = db.Column(db.String(120))
    posts = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', '/']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/')
def display_users():
    usernames = User.query.all()
    return render_template("index.html", usernames=usernames)

@app.route('/singleuser')
def singleuser_posts():
    #Should single user page be handled here or under the blog handler??
    #Trying to get info from query parameter to render singleuser page
    user_id = int(request.args.get('user_id'))
    user_posts = Blog.query.filter_by(user_id=user_id)
    return render_template("singleuser.html", user_posts=user_posts)

@app.route('/logout')
def logout():
    del session['username']
    return redirect('login')

@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/new_post')
        else:
            flash('User password incorrect, or user does not exist')

    return render_template('login.html')

@app.route("/signup", methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        #VALIDATE USERS DATA
        if password != verify or password == '' or len(password) < 3:
            flash('Passwords cannot be left blank and must be greater than 3 characters')
            return redirect("/signup")
            

        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect("/new_post")

        else:
            return "<h1>Duplicate User</h1>"
    return render_template('signup.html')



@app.route("/blog", methods=['POST', 'GET'])
def display_blog():
    #needs to receive info from new_post
    owner = User.query.filter_by(username=session['username']).first()

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        new_post = Blog(title, body, owner)
        db.session.add(new_post)
        db.session.commit()

        all_posts = Blog.query.all()
        last_post = all_posts[-1]
        if new_post == last_post:
            return redirect ('/post_display?id=' + str(new_post.id))
       
    if request.method == 'GET':
        
        all_posts = Blog.query.all()
        return render_template("blog.html", all_posts=all_posts)


        


@app.route("/new_post", methods=['POST', 'GET'])
def create_new_post():
    error = request.args.get('error')
    blog_title = request.args.get('blog_title')
    blog_body = request.args.get('blog_body')
    if error:
        error = error
        blog_title = blog_title
        blog_body = blog_body
    else:
        error = ''
        blog_title = ''
        blog_body = ''
   
    return render_template("new_post.html", error=error, blog_title=blog_title, blog_body=blog_body)

@app.route("/post_display", methods=['POST', 'GET'])
def display_post(): 
    id = request.args.get('id')
    
    blog = Blog.query.get(id)
    user_id = blog.id
    blog_title = blog.title
    blog_body = blog.body
    author = blog.owner.username
    #NEED TO ADD A CREATION DATE/TIME ATTRIBUTE AND ORDER IT IN /BLOG
    if blog_title == '' or blog_body == '':
        error = 'Text fields cannot be left blank'

        return redirect('/new_post?error=' + error + '&blog_title=' + blog_title + '&blog_body=' + blog_body)

    return render_template("post_display.html", user_id=user_id, blog_title=blog_title, blog_body=blog_body, author=author)

if __name__ == '__main__':
    app.run()