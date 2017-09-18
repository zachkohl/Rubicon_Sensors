from flask import Flask, render_template, request, url_for, redirect,flash
from flask_sqlalchemy import SQLAlchemy
from wtforms import Form, BooleanField, StringField, validators,PasswordField
from flask.ext.bcrypt import Bcrypt, generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user


app = Flask(__name__)
bcrypt = Bcrypt(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:kr8tBnnz@localhost:3306/rubiconsensors_0-1'
db = SQLAlchemy(app)

# Login Stuff

class users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String)

    def __init__(self, username, email,password):
        self.username = username
        self.email = email
        self.password = password

    def __repr__(self):
        return '<User %r>' % self.username

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return users.query.get(int(user_id))


@app.route('/')
def home():
    return render_template('home.html')


class RegistrationForm(Form):
    username     = StringField('Username', [validators.Length(min=4, max=25),validators.Required()])
    password     = PasswordField('Password', [validators.Length(min=4, max=25),validators.Required()])

class LoginForm(Form):
    username     = StringField('Username', [validators.Required()])
    password     = PasswordField('Password', [validators.Required()])



@app.route('/register.html', methods = [ "GET", "POST"])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        username = form.username.data
        password = form.password.data
        pw_hash = bcrypt.generate_password_hash(password)
        flash('username "' + username +'" has been added to the database')
        db.engine.execute("INSERT INTO users(username,password) VALUES (%s, %s)",(username, pw_hash))
        return redirect(url_for('register'))
    return render_template('register.html', form= form)



@app.route('/login.html', methods = ['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        username = form.username.data
        inputed_password = form.password.data
        user = users.query.filter_by(username = username).first()
        pw_hash = bcrypt.generate_password_hash(inputed_password) #See https://flask-bcrypt.readthedocs.io/en/latest/
        flash('got to here')
        if check_password_hash( user.password, inputed_password):
            flash('password matches!')
            login_user(user)
        else:
            flash('password failed')

        return redirect(url_for('login'))

    return render_template('login.html', form=form)

@app.route('/dashboard.html')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/logout.html')
@login_required
def logout():
    logout_user()
    return render_template('logout.html')

if __name__ == '__main__':
    app.secret_key="jyooGbO0eXelz9lrRQH6f0FL4r57SRM8"
    app.run(debug=True)
