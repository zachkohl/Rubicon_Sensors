from flask import Flask, render_template, request, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from wtforms import Form, BooleanField, StringField, validators,PasswordField
from werkzeug.security import check_password_hash, generate_password_hash #don't know why this works, have not installed in virtualdev
from wtforms import Form, BooleanField, StringField, validators,PasswordField
from flask.ext.bcrypt import Bcrypt, generate_password_hash, check_password_hash
# from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import gviz_api #google chart api
from flask_sslify import SSLify #force HTTPS






app = Flask(__name__) #Starts the flask application, passes into other stuff. Used to tie the whole website framework together
bcrypt = Bcrypt(app) #use for encryption




####################################################DATABASE STUFF###############################################################
#Just comment out the parts parts you aren't using and remove the comments for the machine you are using. Should work fine. 


#  #DATABASE: use this stuff for Sam's desktop
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:password@localhost:3306/sakila'
# db = SQLAlchemy(app)  




#  DATABASE: use this stuff for Zach's desktop
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:kr8tBnnz@localhost:3306/rubiconsensors_0-1'
#=======
#DATABASE: use this stuff for Zach's desktop
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:kr8tBnnz@localhost:3306/rubiconsensors_0-1'




# DATABASE: use this stuff for deployment on python anywhere. 

sslify = SSLify(app) #Runs SSLify, need this in production to force use of SSL. Don't care in development. 
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


#End database deployment
#######################################SQLACODEGEN STUFF############################################################

#This is all the sqlacodegen stuff Zach and Sam created.
#You can use this DB (i.e. the slqacodegen stuff) or the one below it. Just be sure to comment out whichever one you are not using.
#The sqlacodegen created here is from pip install sqlacodegen, due to the flask-sqlacodegen running into an internal file error. 
#
db.Model = declarative_db.Model()
metadata = db.Model.metadata


class Flowsensor(db.Model):
    __tablename__ = 'flowsensor'

    idFlowSensor = Column(Integer, primary_key=True, nullable=False)
    Payer_PayerID = Column(ForeignKey('payer.PayerID'), primary_key=True, nullable=False, index=True)
    Address = Column(String(100))

    payer = db.relationship('Payer')
    viewer = db.relationship('Viewer', secondary='viewer_has_flowsensor')


class Flowsensordata(db.Model):
    __tablename__ = 'flowsensordata'

    idFlowSensor = Column(Integer, primary_key=True, nullable=False)
    ISO8601 = Column(String(100))
    Data = Column(Integer)
    FlowSensor_idFlowSensor = Column(ForeignKey('flowsensor.idFlowSensor'), primary_key=True, nullable=False, index=True)

    flowsensor = db.relationship('Flowsensor')


class Payer(db.Model):
    __tablename__ = 'payer'

    PayerID = Column(Integer, primary_key=True, unique=True)
    UserName = Column(String(45))
    Email = Column(String(90))
    FirstName = Column(String(45))
    LastName = Column(String(45))
    Password = Column(String(100))
    register_date = Column(String(100))


class User(db.Model):
    __tablename__ = 'user'
    __table_args__ = (
        ForeignKeyConstraint(['Viewer_idViewer', 'Viewer_Payer_PayerID'], ['viewer.idViewer', 'viewer.Payer_PayerID']),
        Index('fk_User_Viewer1_idx', 'Viewer_idViewer', 'Viewer_Payer_PayerID')
    )

    idUser = Column(Integer, primary_key=True, nullable=False)
    Email = Column(String(45))
    Name = Column(String(45))
    FirstName = Column(String(45))
    LastName = Column(String(45))
    Address = Column(String(45))
    Password = Column(String(45))
    UserName = Column(String(45))
    Usercol = Column(String(45))
    Viewer_idViewer = Column(Integer, primary_key=True, nullable=False)
    Viewer_Payer_PayerID = Column(Integer, primary_key=True, nullable=False)
    Payer_PayerID = Column(ForeignKey('payer.PayerID'), primary_key=True, nullable=False, index=True)

    payer = db.relationship('Payer')
    viewer = db.relationship('Viewer')


class Viewer(db.Model):
    __tablename__ = 'viewer'

    idViewer = Column(Integer, primary_key=True, nullable=False)
    PayerID = Column(Integer)
    Login = Column(String(45))
    FirstName = Column(String(45))
    LastName = Column(String(45))
    Email = Column(String(90))
    Payer_PayerID = Column(ForeignKey('payer.PayerID'), primary_key=True, nullable=False, index=True)

    payer = db.relationship('Payer')


t_viewer_has_flowsensor = Table(
    'viewer_has_flowsensor', metadata,
    Column('Viewer_idViewer', ForeignKey('viewer.idViewer'), primary_key=True, nullable=False, index=True),
    Column('FlowSensor_idFlowSensor', ForeignKey('flowsensor.idFlowSensor'), primary_key=True, nullable=False, index=True)
)


    def __init__(self, username, email,password):
        self.username = username
        self.email = email
        self.password = password

    def __repr__(self):
        return '<User %r>' % self.username

########################################END DATABASE STUFF########################################################



# #Other database models
#     #Create a model of the database for use in python
# class pipe_sensor(db.Model): #The name is the name from the SQL database. This is not about setting up a SQL database!
#                                #It is about creating a local model of the far away SQL database
#                                #We pass in db.model because that will turn the class into something that SQLAlchemy can use SPECIAL TO FLASK SQLALCHEMY
#                                #Recall  db = SQLAlchemy(app)
#     __tablename__ = "pipe_sensor" #The name of the actual SQL table that this local python class is going to represent
#     id = db.Column('id', db.Integer, primary_key=True) #Describes the first column.
#                                                                 #Input arguments are the column name, what the datatype is, and if it is a primary key
#                                                                 #Don't have to worry about auto imcrement normally because SQL does that automatically. See http://docs.sqlalchemy.org/en/latest/core/metadata.html#sqlalchemy.schema.Column.params.onupdate

#     ISO8601 = db.Column('ISO8601', db.String)                   #descriptions of the other columns, for explanation of legal data types, see https://dev.mysql.com/doc/refman/5.7/en/numeric-types.html
#                                                                 #Recall also that this is flask-SQLAlchemy, so google the docs for more info.
#     data = db.Column('data', db.Integer)
#     timestamp = db.Column('timestamp', db.String)

#     #We now have a map for SQLAlchemy to use to relate tot the database. This will let us do all the fun SQLAlchemy commands to electron1
#     # or whatever we name it. Things like pipe_sensor.query.all() See functions for use examples.

###################################################LOGIN STUFF######################################################
#See https://blog.pythonanywhere.com/158/

#Step 1, make sure secrete key is inplace, ours is at the bottom of this document

login_manager = LoginManager() #Create an instance of Flask-Login
login_manager.init_app(app) #Associate the instance with the fask app

#These are forms that are used later. use tools from wtforms
class RegistrationForm(Form):
    username     = StringField('Username', [validators.Length(min=4, max=25),validators.Required()])
    password     = PasswordField('Password', [validators.Length(min=4, max=25),validators.Required()])

class LoginForm(Form):
    username     = StringField('Username', [validators.Required()])
    password     = PasswordField('Password', [validators.Required()])

#Create user class that will tell us something about the users

class User(UserMixin):
 #By passing in the "UserMixin" we inherit all the abilities of the UserMixin class
#Page 408-409 in the python book explains this really well.
#The "User" class can now use all the properties and methods of the UserMixin superclass

    #The following methods will be true for each instantation of "User"
    #in addition to all the methods that are already present from the UserMixin superclass.
    #Each method has attributes underneath it.

    #The __init__ is called aa constructor. We can only have one per class. Page 372 in the book
    #talks about this. This is a special function that will be called as soon as the "User" object
    #is created.
    #Within the parantheses, the first parameter must be a reference to the object itself. By convention
    #this is named "self."
    #Self can now be used inside the class to refer to the object itself. This is just special notation
    #that has to be this way because of the way python is set up.
    def __init__(self, username, password_hash):
        self.username = username
        self.password_hash = password_hash

    #The following methods now exist for use with each "User" object. They return things when called.
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    #Notice how get_id refers to the object iself using "self"
    def get_id(self):
        return self.username


#Below is the database stuff
class users(UserMixin, db.Model):
     #This is how you make a new table in SQL Alchemy. It is a table that represents a table in SQL.
     #See https://www.pythoncentral.io/introductory-tutorial-python-sqlalchemy/
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

#The following decorator is required in the flask login instructions. It helps the login make sure
#it is loggging in the correct the user.
@login_manager.user_loader
def load_user(user_id):
    return users.query.get(int(user_id))



@app.route("/login/", methods =["GET", "POST"]) #Allow for post methods (RESTful API stuff)
def login():

    form = LoginForm(request.form) #local version of form.
    if request.method == 'POST':
        #If it is the post method, then use the RESTful API form stuff (A sub part of POST) as variables
        username = form.username.data
        inputed_password = form.password.data
        user = users.query.filter_by(username = username).first() #Do a database query of the username
        pw_hash = bcrypt.generate_password_hash(inputed_password) #Create a password hash to compare #See https://flask-bcrypt.readthedocs.io/en/latest/

        if user:
            #If the user object got created by the database, then do this stuff
            if check_password_hash( user.password, inputed_password):
                #Like check the password
                #And log in the user
                login_user(user)
                return redirect(url_for('dashboard'))
            else:
                #flash('password failed')
                return redirect(url_for('login'))


        else:
            return redirect(url_for('login'))

    return render_template('login.html', form=form)
    #
    # if request.method == "GET":
    #     return render_template("login.html", error=False) #This if statement says just load the page if all they want to do is see it (GET method)
    #
    # username = request.form["username"] #The form method is part of the POST method. This line of code just puts the username value from the form
    #                                     #(I think it is another dictionary) into a more usable variable
    # if username not in all_users:
    #     #This if statement checks if the username from the form is in the all_users dictionary. If it is not, it loads the page but turns the error flag to true.
    #     return render_template("login.html", error=True)
    # user = all_users[username] #This pulls out (creates a specific copy) of the correct user object stored in all users that corresponds to the inputed username
    #                            #Note this local object has a LOWERCASE! The class has an uppercase.
    #
    # if not user.check_password(request.form["password"]):
    #     #The if not checks for true/false. Recall the check_password method was created earlier when we defined the user subclass of the UserMixin Superclass.
    #     #It takes the password from the form (sumitted by POST) and passes it into the check_password method. Returns true or false becuase that is what the check_password_hash
    #     #method does. We imported check_password_hash from a library.
    #     return redirect('/dashboard.html') #render_template("login_page.html", error=True) #IF the user.check_password is NOT true (bad password), send them back to the template with the error flag raised.
    #
    # login_user(user)
    #
    # #If we make it to this line without sending the user off with a "return" which I think ends the function, we get to use the library imported login_user object.
    #                  #Pass the user object into it so it logs in the right person.
    # return redirect('/')
    # #Now that the individual is logged in, send them off to user logged in land (the dashboard).
    #                                   #Using dashboard.html is a slight variation from the instructions.

#The register function is very similar to login. But it stores into a database rather than doing a query.
@app.route('/register.html', methods = [ "GET", "POST"])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST'and form.validate():
        username = form.username.data
        password = form.password.data
        pw_hash = bcrypt.generate_password_hash(password)

        db.engine.execute("INSERT INTO users(username,password) VALUES (%s, %s)",(username, pw_hash))
        #flash('something got added!')
        return redirect(url_for('home'))
    return render_template('register.html', form= form)

@app.route('/logout.html')
#This is pretty simple, we just call the library included logout_user()
def logout():
    logout_user()
    return render_template('logout.html')

###################################################END LOGIN STUFF##################################################



#This is the login
@app.route('/')
def home():
    return render_template('home.html')










@app.route('/dashboard.html')
@login_required #This makes this page require the user to be logged in to see it.
def dashboard():
#This is the homepage. Doing experiments. See http://banjolanddesign.com/flask-google-charts.html
            # See https://www.codementor.io/sheena/understanding-sqlalchemy-cheat-sheet-du107lawl
            # See https://www.youtube.com/watch?v=Tu4vRU4lt6k
            #http://flask-sqlalchemy.pocoo.org/2.3/quickstart/
    chartdata = pipe_sensor.query.all() #This returns a lists of dictionaries. Each item in the list is a dictionary (dictionary = key-value pair)
                                        #The key-value pair can then ben accessed using dot (like chartdata[0].key) noation or ["key"] notation. ( like chartdata[0]["key"])
                                        #The key is always the header to that column.
                                        #Lists can be iterated over, dictionaries can't. However, lists cannot access their items using dot notation.
                                        #This explains why one must first read the row, then the column. Remember Roman Catholics.



    #The following three lines are how one gets a column out of this thing.
    array_ISO8601 = [] #prep the empty list
    for items in chartdata: #Iteration will cycle through each row
        array_ISO8601.append(items.ISO8601) #use dot notation to only view one column of each row you are iterating over
        #Result is all the other columns are removed and the list now only has one column to it. ``

    array_data = []
    for items in chartdata:
        array_data.append(float(items.data))
        #Exlpanation on float(str())
        # Recall that javascript stores all numbers as just a 'number'.
        # A number in javascript is always a floating point number. Google charts is javascript,
        # so we need to get the decimals from mysql into a format javascript can understand. The float()
        # function does not work on raw mysql decimals, so first to a string, then to a float. Seems to work
        # pretty well.



    return render_template('dashboard.html',array_ISO8601=array_ISO8601,data=array_data) #Pass arrays containing columns to the javascript




@app.route('/input.html', methods = ['GET', 'POST']) #This function is for the particle webhook
def particle():

    if request.method == 'POST':
        webhook = request.form   #see http://flask.pocoo.org/docs/0.12/api/#flask.Request
        data = webhook['data']   #look inside the multidict
        ISO8601 = webhook['published_at']


        db.engine.execute("INSERT INTO pipe_sensor(ISO8601,data) VALUES (%s, %s)",(ISO8601, data))
        return redirect(url_for('register'))

    return render_template('input.html')

app.secret_key="jyooGbO0eXelz9lrRQH6f0FL4r57SRM8"
if __name__ == '__main__':

    app.run(debug=True)
