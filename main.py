from flask import Flask, request, redirect, render_template, session

from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:vs3AJ8ph3gjyIbTc@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'jajhdhkjfidjn'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    body = db.Column(db.String(2000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, name, body, owner):
        self.name = name
        self.body = body 
        self.owner = owner


class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogz = db.relationship('Blog', backref='owner')

    def __init__(self, email, password):
        self.email = email
        self.password = password



@app.before_request
def require_login():
    allowed_routes = ['login', 'sign_up', 'list_blogs', 'index']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')


@app.route('/login', methods=['POST', 'GET'])
def login():

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        email_error = ''
        password_error = ''

        if not user:
            email_error = 'The entered e-mail has not been registered'

        else:
            if user.password != password:
                password_error = 'The password you entered does not match our records'

        if not email_error and not password_error:
            session['email'] = email
            return redirect('/newpost')
        else:
            return render_template('login.html', 
            email_error=email_error,
            password_error=password_error,
            password='',
            email=email)


    return render_template('login.html')

@app.route('/sign_up', methods=['POST', 'GET'])
def sign_up():

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']
        email_error = ''
        password_error = ''
        verify_error = ''
        existing_user = User.query.filter_by(email=email).first()

        if not email:
            email_error = 'Please enter an email'
            email = ''
        else: 
            if ' ' in email:
                email_error = 'Email may not contain any spaces'
            else:                   
                if len(email) < 3 or len(email) > 30:
                    email_error = 'Email length out of range (3-30)'
                else:
                    if existing_user:
                        email_error = 'Email has already been registered'
                        email = ''    
        if not password:
            password_error = 'Please enter a password'            
        else: 
            if ' ' in password :
                password_error = 'Password may not contain any spaces'
            else:                   
                if len(password) < 3 or len(password) > 20:
                    password_error = 'Password length out of range (3-20)'

        if not verify:
            verify_error = 'Please enter your password into the verify password field'            
        else: 
            if verify != password:
                verify_error = 'Your password inputs do not match'

       
        if (not email_error and not password_error 
        and not verify_error):
            new_user = User(email, password)
            db.session.add(new_user)
            db.session.commit()
            session['email'] = email
            return redirect('/newpost')

        else:        
            return render_template('sign_up.html',            
            password_error=password_error,
            verify_error=verify_error,
            email_error=email_error,
            password='',
            verify='',
            email=email)

  

    return render_template('sign_up.html')



@app.route('/logout')
def logout():
    del session['email']
    return redirect('/') 



@app.route('/blog', methods=['POST', 'GET'])
def list_blogs():

    blogs = Blog.query.all()    
    blog_id = (request.args.get('blog_id'))
    users = User.query.all()
    user_id = (request.args.get('user_id'))
    
    if blog_id:
        blog_id = int(blog_id)
        blog = Blog.query.filter_by(id=blog_id).first()
        blog_title = blog.name
        blog_body = blog.body
       

        return render_template('blog_post.html', 
        blog=blog)

    if user_id:
        user_id = int(user_id)   
        user = User.query.filter_by(id=user_id).first()
        user_blogs = Blog.query.filter_by(owner_id=user_id).all()
        
        return render_template('user_page.html', title=user.email + ' blog page', 
        user_blogs=user_blogs,
        header=user.email + "'s Blog Page" )


    if not blog_id and not user_id:
        return render_template('all_blogs.html', title='Build a Blog!',
    blogs=blogs, header="Blogz!")
   

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():

    owner = User.query.filter_by(email=session['email']).first()

    if request.method == 'POST':
        blog_title = request.form['blog_title']
        blog_body = request.form['blog_body']
       
        blog_body_error = ""
        blog_title_error = ""


        if not blog_title:
            blog_title_error = "Please enter a title"

        if not blog_body:
            blog_body_error = "Please enter some text in the body"    
       
        
        if (not blog_title_error and not blog_body_error):

            new_post = Blog(blog_title, blog_body, owner)
            db.session.add(new_post)
            db.session.commit()
            blog_id = new_post.id 
            return redirect('/blog?blog_id={0}'.format(blog_id))
        
        else:
            return render_template('new_post.html', 
            blog_title_error=blog_title_error,
            blog_body_error=blog_body_error,
            blog_title=blog_title,
            blog_body=blog_body)
        

    return render_template('new_post.html', title='New Post')    

@app.route('/')
def index():
    users = User.query.all()

    return render_template('index.html', title='Home',
    header='Home Page',
     users=users)

@app.route('/blog')
def blog_post():
    blog_id = int(request.args.get('blog_id'))
    blog = Blog.query.filter_by(id=blog_id).first()
    blog_title = blog.name
    blog_body = blog.body

    return render_template('blog_post.html', 
    blog_title=blog_title, 
    blog_body=blog_body)

















if __name__ =='__main__':
    app.run()