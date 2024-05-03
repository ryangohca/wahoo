import random, string, os
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

class UploadForm(FlaskForm):
    photos = MultipleFileField('Image', validators=[
        Optional(),
        FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')
    ])
    rate = IntegerField("Rate", validators=[InputRequired(), NumberRange(min=1, max=5)])
    description = TextAreaField("Description", validators=[InputRequired()])
    tags = SelectMultipleField(
        'Tags (ctrl-click to select multiple tags):',
        validators=[Optional()],
        choices=[
            ('Western', 'Western'),
            ('Japanese', 'Japanese'),
            ('Chicken Rice', 'Chicken Rice')
        ])

# databases
db = SQLAlchemy(app)
class Posts(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    description = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    tags = db.Column(db.Text, nullable=False)
    images = db.relationship('Images', backref='posts', lazy=True)

class Images(db.Model):
    __tablename__ = 'images'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    postID = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    imagePath = db.Column(db.String(100), nullable=False)

# routes + other functions
def generateRandomName(length=30):
    return ''.join(random.choice(string.ascii_letters + string.digits) for i in range(length))

@app.route('/')
def root():
    return render_template("home.html")

@app.route('/reseteverything')
def reseteverything():
    __refresh()
    return redirect(url_for('root'))

@app.route('/login')
def login():
    return render_template('login.html', loginForm=LoginForm())

@app.route('/upload', methods=["GET", "POST"])
def upload():
    uploadForm = UploadForm()
    if request.method == "POST":
        if uploadForm.validate_on_submit():
            description = uploadForm.description.data
            rating = uploadForm.rate.data
            tags = ','.join(uploadForm.tags.data)
            post = Posts(description=description, rating=rating, tags=tags)
            db.session.add(post)
            db.session.commit()

            for file in uploadForm.photos.data:
                filename = secure_filename(file.filename)
                new_filename = generateRandomName() + '.' + filename.split('.')[-1]
                full_path = os.path.abspath(Path(app.config['UPLOAD_FOLDER']) / new_filename)
                file.save(full_path)
                image = Images(postID=post.id, imagePath=full_path)
                db.session.add(image)
                db.session.commit()
            
            return render_template('upload.html', uploadForm=UploadForm(), success=True)

    return render_template('upload.html', uploadForm=uploadForm)

def __refresh():
    db.drop_all()
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True) #to remove after everything is done
