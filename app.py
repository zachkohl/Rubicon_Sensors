from flask import Flask, render_template, request, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from wtforms import Form, BooleanField, StringField, validators,PasswordField
from flask.ext.bcrypt import Bcrypt, generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import gviz_api #google chart api



app = Flask(__name__)
bcrypt = Bcrypt(app)

# DATABASE: use this stuff for local desktop
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:kr8tBnnz@localhost:3306/rubiconsensors_0-1'
#db = SQLAlchemy(app)


# DATABASE: use this stuff for deployment on python anywhere
SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
     username="rubiconsensors",
     password="wf5PWRM4",
     hostname="rubiconsensors.mysql.pythonanywhere-services.com",
     databasename="rubiconsensors$riversensedb",
 )
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
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


#@app.route('/')
#def home():
#    dbResults = db.engine.execute("SELECT * FROM chartdata")
#    return render_template('home.html',dbResults=dbResults)


class RegistrationForm(Form):
    username     = StringField('Username', [validators.Length(min=4, max=25),validators.Required()])
    password     = PasswordField('Password', [validators.Length(min=4, max=25),validators.Required()])

class LoginForm(Form):
    username     = StringField('Username', [validators.Required()])
    password     = PasswordField('Password', [validators.Required()])

class InputForm(Form):
    year         = StringField()
    probe1       = StringField()
    probe5       = StringField()
    data         = StringField()


@app.route('/register.html', methods = [ "GET", "POST"])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST'and form.validate():
        username = form.username.data
        password = form.password.data
        pw_hash = bcrypt.generate_password_hash(password)

        db.engine.execute("INSERT INTO users(username,password) VALUES (%s, %s)",(username, pw_hash))
        #flash('something got added!')
        return redirect(url_for('register'))
    return render_template('register.html', form= form)



@app.route('/login.html', methods = ['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST':
        username = form.username.data
        inputed_password = form.password.data
        user = users.query.filter_by(username = username).first()
        pw_hash = bcrypt.generate_password_hash(inputed_password) #See https://flask-bcrypt.readthedocs.io/en/latest/
        if user:
            if check_password_hash( user.password, inputed_password):
                login_user(user)
                return redirect(url_for('dashboard'))
            else:
                #flash('password failed')
                return redirect(url_for('login'))
        else:
            return redirect(url_for('login'))

    return render_template('login.html', form=form)

@app.route('/') #have this set to be the home page
#@login_required #makes it so the dashboard can only be seen when logged in
def dashboard():
    dbResults = db.engine.execute("SELECT * FROM chartdata")
    description = {"year": ("string", "year"),"probe1": ("number", "probe1"),"probe5": ("number", "probe5")} #This is the headers for the google chart

    data=[] #create empty array
    for row in dbResults:
        items = {'year': row['year'], 'probe1': row['probe1'], 'probe5':row['probe5']} #recall a table is an array of arrays
        data.append(items) #load array

    #Load into google charts systems to output a JSON string that can be used by Google charts
    data_table = gviz_api.DataTable(description)
    data_table.LoadData(data)
    json = data_table.ToJSon(columns_order=("year", "probe1","probe5"), order_by="year")

    return render_template('dashboard.html',json=json) #pass json object off to template for rendering

@app.route('/logout.html')
@login_required
def logout():
    logout_user()
    return render_template('logout.html')


@app.route('/input.html', methods = ['GET', 'POST']) #This function is for the particle webhook
def particle():
   # form = InputForm(request.form) #for use with human html interface
    year = 1
    if request.method == 'POST':
        data = request.form   #see http://flask.pocoo.org/docs/0.12/api/#flask.Request
        temp = data['data']   #look inside the multidict

        year = year+1
        probe5 = 10
        #year = form.year.data #for use with human html interface
        #probe1=form.probe1.data #for use with human html interface
        #probe5=form.probe5.data #for use with human html interface
        #db.engine.execute("INSERT INTO chartdata(year,probe1,probe5) VALUES (%s, %s, %s)",(year, data,probe5)) #for use with human html interface
        db.engine.execute("INSERT INTO chartdata(year,probe1, probe5) VALUES (%s, %s, %s)",(year, temp, probe5))
        return redirect(url_for('register'))

    return render_template('input.html')


if __name__ == '__main__':
    app.secret_key="jyooGbO0eXelz9lrRQH6f0FL4r57SRM8"
    app.run(debug=True)
