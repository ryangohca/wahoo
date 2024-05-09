import random, string, os, re
from pathlib import Path

from flask import Flask, render_template, request, redirect, url_for

from flask_wtf import FlaskForm
from flask_wtf.file import MultipleFileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, BooleanField, HiddenField, IntegerField, TextAreaField, SelectMultipleField
from wtforms.validators import InputRequired, ValidationError, NumberRange, Optional
from werkzeug.utils import secure_filename

from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# configs
app.config['SECRET_KEY'] = "cutechodan" # yeah not supposed to have secret key in source code but who cares

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///app.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Optimisation
app.config['SQLALCHEMY_ECHO'] = True # See all sql statements that are being run

app.config['UPLOAD_FOLDER'] = "static/images/posts"

# Forms

class LoginForm(FlaskForm):
    username = StringField('Username', id="login-username", validators=[InputRequired()])
    password = PasswordField('Password', id="login-password", validators=[InputRequired()])
    remember_me = BooleanField('Remember Me', id="login-remember_me")
    
    formName = HiddenField(default="login", id="login-formName")
    
    def validate_username(form, field):
        username = field.data.strip()
        pass
            
    def validate_password(form, field):
        password = field.data.strip()
        pass

class SignUpForm(FlaskForm):
    username = StringField('Username', id="signup-username", validators=[InputRequired()])
    password = PasswordField('Password', id="signup-password", validators=[InputRequired()])
    repeatPassword = PasswordField('Repeat Password', id="signup-password", validators=[InputRequired()])
    formName = HiddenField(default="signup", id="signup-formName")
    
    def validate_username(form, field):
        username = field.data.strip()
        pass
            
    def validate_password(form, field):
        password = field.data.strip()
        pass

class UploadForm(FlaskForm):
    photos = MultipleFileField('Image', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')
    ])
    title = StringField("Title", validators=[InputRequired()])
    rate = IntegerField("Rate", validators=[InputRequired(), NumberRange(min=1, max=5)])
    description = TextAreaField("Description", validators=[InputRequired()])
    tags = SelectMultipleField(
        'Tags (ctrl-click to select multiple tags):',
        validators=[InputRequired()],
        choices=[
            ('Western', 'Western'),
            ('Japanese', 'Japanese'),
            ('Chicken Rice', 'Chicken Rice'),
            ('Noodle', 'Noodle'),
            ('Bread','Bread'),
            ('Drinks','Drinks'),
            ('Others','Others')
        ])

# databases
db = SQLAlchemy(app)
class Posts(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    url_title = db.Column(db.Text, unique=True, nullable=False)
    title = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    tags = db.Column(db.Text, nullable=False)
    images = db.relationship('Images', backref='posts', lazy=True)

class Images(db.Model):
    __tablename__ = 'images'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    postID = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    imageName = db.Column(db.String(100), nullable=False)

# routes + other functions
def generateRandomName(length=30):
    return ''.join(random.choice(string.ascii_letters + string.digits) for i in range(length))

def generateUniqueUrl(title):
    url = '_'.join(title.lower().strip().split(' '))
    pattern = '[^a-zA-Z0-9-_]'
    friendly_url = ''.join(re.split(pattern, url))
    if Posts.query.filter_by(url_title=friendly_url).first() is not None:
        additional_num = 2
        while Posts.query.filter_by(url_title=friendly_url + '_' + str(additional_num)).first() is not None:
            additional_num += 1
        friendly_url += '_' + str(additional_num)
    return friendly_url    

@app.route('/',methods=['GET','POST'])
def root():
    contents = []
    posts = []
    if request.method == "POST":
        if 'search' in request.form:
            posts = Posts.query.filter(Posts.description.like(f"%{request.form['item']}%")).order_by(Posts.id.desc()).all()
    else:
        posts = Posts.query.order_by(Posts.id.desc())
    for post in posts:
        ID = post.id
        image = Images.query.filter_by(postID=ID).first().imageName
        description = post.description[:150] + '...'
        contents.append((post, image, description))  #not done yet tryna figure out images
    return render_template("home.html", contents=contents)


# uncomment if need to reset stuff
@app.route('/reseteverything')
def reseteverything():
    db.drop_all()
    db.create_all()
    return redirect(url_for('root'))


@app.route('/login')
def login():
    return render_template('login.html', loginForm=LoginForm())

@app.route('/signup')
def signup():
    return render_template('signup.html', signUpForm=SignUpForm())

@app.route('/upload', methods=["GET", "POST"])
def upload():
    uploadForm = UploadForm()
    if request.method == "POST":
        if uploadForm.validate_on_submit():
            description = uploadForm.description.data
            title = uploadForm.title.data
            rating = uploadForm.rate.data
            tags = ','.join(uploadForm.tags.data)
            url_title = generateUniqueUrl(title)
            post = Posts(url_title=url_title, title=title, description=description, rating=rating, tags=tags)
            db.session.add(post)
            db.session.commit()

            for file in uploadForm.photos.data:
                filename = secure_filename(file.filename)
                new_filename = generateRandomName() + '.' + filename.split('.')[-1]
                full_path = os.path.abspath(Path(app.config['UPLOAD_FOLDER']) / new_filename)
                file.save(full_path)
                image = Images(postID=post.id, imageName=new_filename)
                db.session.add(image)
                db.session.commit()
            
            return render_template('upload.html', uploadForm=UploadForm(), success=True)

    return render_template('upload.html', uploadForm=uploadForm)

@app.route('/post/<url_title>')
def post(url_title):
    user_post = Posts.query.filter_by(url_title=url_title).first()
    if user_post is None:
        return "Page Not Found", 404
    images = [image.imageName for image in Images.query.filter_by(postID=user_post.id).all()]
    tags = user_post.tags.split(',')
    return render_template("post.html", post=user_post, images=images, tags=tags)

@app.route('/surprise')
def surprise():
    posts_url = [post.url_title for post in Posts.query]
    url = random.choice(posts_url)
    return redirect(url_for('post', url_title=url))

if __name__ == '__main__':
    app.run(debug=True) #to remove after everything is done
