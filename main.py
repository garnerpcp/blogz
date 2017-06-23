from flask import Flask, request, redirect, render_template

from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:BKsPWOqC2OKU47dP@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    body = db.Column(db.String(2000))

    def __init__(self, name, body):
        self.name = name
        self.body = body 

@app.route('/blog', methods=['POST', 'GET'])
def index():

    blogs = Blog.query.all()    
    blog_id = (request.args.get('blog_id'))
    if not blog_id:
        return render_template('main_form.html', title='Build a Blog!',
    blogs=blogs, header="Build a Blog!")
    else:
        blog_id = int(blog_id)
        blog = Blog.query.filter_by(id=blog_id).first()
        blog_title = blog.name
        blog_body = blog.body

        return render_template('blog_post.html', 
        blog_title=blog_title, 
        blog_body=blog_body)

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():

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

            new_post = Blog(blog_title, blog_body)
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