from flask import Flask, render_template

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, BooleanField, HiddenField, IntegerField, TextAreaField, SelectMultipleField
from wtforms.validators import InputRequired, ValidationError, NumberRange, Optional

app = Flask(__name__)
app.config['SECRET_KEY'] = "cutechodan" # yeah not supposed to have secret key in source code but who cares

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
    photo = FileField('Image', validators=[
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

@app.route('/')
def root():
    return render_template("home.html")

@app.route('/login')
def login():
    return render_template('login.html', loginForm=LoginForm())

@app.route('/upload')
def upload():
    return render_template('upload.html', uploadForm=UploadForm())

if __name__ == '__main__':
    app.run(debug=True) #to remove after everything is done
