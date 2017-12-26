from flask import Flask, render_template, request, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_user, LoginManager, UserMixin
from werkzeug.security import check_password_hash, generate_password_hash #don't know why this works, have not installed in virtualdev
from wtforms import Form, BooleanField, StringField, validators,PasswordField
from flask.ext.bcrypt import Bcrypt, generate_password_hash, check_password_hash
#from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import gviz_api #google chart api






app = Flask(__name__) #Starts the flask application, passes into other stuff. Used to tie the whole website framework together


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
#End database deployment



#Other database models
    #Create a model of the database for use in python
class electron1(db.Model): #The name is the name from the SQL database. This is not about setting up a SQL database!
                               #It is about creating a local model of the far away SQL database
                               #We pass in db.model because that will turn the class into something that SQLAlchemy can use SPECIAL TO FLASK SQLALCHEMY
                               #Recall  db = SQLAlchemy(app)
    __tablename__ = "electron1" #The name of the actual SQL table that this local python class is going to represent
    id = db.Column('id', db.Integer, primary_key=True) #Describes the first column.
                                                                #Input arguments are the column name, what the datatype is, and if it is a primary key
                                                                #Don't have to worry about auto imcrement normally because SQL does that automatically. See http://docs.sqlalchemy.org/en/latest/core/metadata.html#sqlalchemy.schema.Column.params.onupdate

    ISO8601 = db.Column('ISO8601', db.String)                   #descriptions of the other columns
    probe1 = db.Column('probe1', db.Numeric)
    probe2 = db.Column('probe2', db.Numeric)
    probe3 = db.Column('probe3', db.Numeric)
    probe4 = db.Column('probe4', db.Numeric)
    probe5 = db.Column('probe5', db.Numeric)
    timestamp = db.Column('timestamp', db.String)

    #We now have a map for SQLAlchemy to use to relate tot the database. This will let us do all the fun SQLAlchemy commands to electron1
    # or whatever we name it. Things like electron1.query.all() See functions for use examples.

###################################################LOGIN STUFF######################################################
#See https://blog.pythonanywhere.com/158/

#Step 1, make sure secrete key is inplace, ours is at the bottom of this document

login_manager = LoginManager() #Create an instance of Flask-Login
login_manager.init_app(app) #Associate the instance with the fask app


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
    #Within the parantheses, the first parameter must be a reference to teh object itself. By convention
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


#Now lets define some users. Notice that the username and password variables pass into user, which passes into UserMixin
# We use a dictionary so we can use the functionality of key-value pairing later on.
all_users = {
    "admin": User("admin", generate_password_hash("secret")),
    "bob": User("bob", generate_password_hash("less-secret")),
    "caroline": User("caroline", generate_password_hash("completely-secret")),
}

@login_manager.user_loader #This is a decorator, it dynamically updates the login manager class without using a subcass. See https://wiki.python.org/moin/PythonDecorators
def load_user(user_id):
    return all_users.get(user_id) #All users is a dictionary (key-value pair) and get is a method on dictionaries that selects a key and returns that value.
                                  #This is how we access the "user" object that has been instatiated and using the above code.

@app.route("/login/", methods =["GET", "POST"]) #Allow for post methods (RESTful API stuff)
def login():
    if request.method == "GET":
        return render_template("login_page.html", error=False) #This if statement says just load the page if all they want to do is see it (GET method)

    username = request.form["username"] #The form method is part of the POST method. This line of code just puts the username value from the form
                                        #(I think it is another dictionary) into a more usable variable
    if username not in all_users:
        #This if statement checks if the username from the form is in the all_users dictionary. If it is not, it loads the page but turns the error flag to true.
        return render_template("login_page.html", error=True)
    user = all_users[username] #This pulls out (creates a specific copy) of the correct user object stored in all users that corresponds to the inputed username
                               #Note this local object has a LOWERCASE! The class has an uppercase.

    if not user.check_password(request.form["password"]):
        #The if not checks for true/false. Recall the check_password method was created earlier when we defined the user subclass of the UserMixin Superclass.
        #It takes the password from the form (sumitted by POST) and passes it into the check_password method. Returns true or false becuase that is what the check_password_hash
        #method does. We imported check_password_hash from a library.
        return redirect('/dashboard.html') #render_template("login_page.html", error=True) #IF the user.check_password is NOT true (bad password), send them back to the template with the error flag raised.

    login_user(user)

    #If we make it to this line without sending the user off with a "return" which I think ends the function, we get to use the library imported login_user object.
                     #Pass the user object into it so it logs in the right person.
    return redirect('/')
    #Now that the individual is logged in, send them off to user logged in land (the dashboard).
                                      #Using dashboard.html is a slight variation from the instructions.


###################################################END LOGIN STUFF##################################################




@app.route('/')
def home():

    return render_template('home.html')




class InputForm(Form):
    year         = StringField()
    probe1       = StringField()
    probe5       = StringField()
    data         = StringField()








@app.route('/dashboard.html') #have this set to be the home page
#@login_required #makes it so the dashboard can only be seen when logged in
def dashboard():
#This is the homepage. Doing experiments. See http://banjolanddesign.com/flask-google-charts.html
            # See https://www.codementor.io/sheena/understanding-sqlalchemy-cheat-sheet-du107lawl
            # See https://www.youtube.com/watch?v=Tu4vRU4lt6k
            #http://flask-sqlalchemy.pocoo.org/2.3/quickstart/
    chartdata = electron1.query.all() #This returns a lists of dictionaries. Each item in the list is a dictionary (dictionary = key-value pair)
                                        #The key-value pair can then ben accessed using dot (like chartdata[0].key) noation or ["key"] notation. ( like chartdata[0]["key"])
                                        #The key is always the header to that column.
                                        #Lists can be iterated over, dictionaries can't. However, lists cannot access their items using dot notation.
                                        #This explains why one must first read the row, then the column. Remember Roman Catholics.



    #The following three lines are how one gets a column out of this thing.
    array_ISO8601 = [] #prep the empty list
    for items in chartdata: #Iteration will cycle through each row
        array_ISO8601.append(items.ISO8601) #use dot notation to only view one column of each row you are iterating over
        #Result is all the other columns are removed and the list now only has one column to it. ``

    array_probe1 = []
    for items in chartdata:
        array_probe1.append(float(str(items.probe1)))
        #Exlpanation on float(str())
        # Recall that javascript stores all numbers as just a 'number'.
        # A number in javascript is always a floating point number. Google charts is javascript,
        # so we need to get the decimals from mysql into a format javascript can understand. The float()
        # function does not work on raw mysql decimals, so first to a string, then to a float. Seems to work
        # pretty well.
    array_probe2 = []
    for items in chartdata:
        array_probe2.append(float(str(items.probe2)))

    array_probe3 = []
    for items in chartdata:
        array_probe3.append(float(str(items.probe3)))

    array_probe4 = []
    for items in chartdata:
        array_probe4.append(float(str(items.probe4)))

    array_probe5 = []
    for items in chartdata:
        array_probe5.append(float(str(items.probe5)))


    return render_template('dashboard.html',array_ISO8601=array_ISO8601,array_probe1=array_probe1,array_probe2=array_probe2,array_probe3=array_probe3,array_probe4=array_probe4,array_probe5=array_probe5) #Pass arrays containing columns to the javascript




@app.route('/input.html', methods = ['GET', 'POST']) #This function is for the particle webhook
def particle():
   # form = InputForm(request.form) #for use with human html interface
    year = 1
    if request.method == 'POST':
        webhook = request.form   #see http://flask.pocoo.org/docs/0.12/api/#flask.Request
        data = webhook['data']   #look inside the multidict

        year = year+1
        probe5 = 10
        #year = form.year.data #for use with human html interface
        #probe1=form.probe1.data #for use with human html interface
        #probe5=form.probe5.data #for use with human html interface
        #db.engine.execute("INSERT INTO chartdata(year,probe1,probe5) VALUES (%s, %s, %s)",(year, data,probe5)) #for use with human html interface
        #db.engine.execute("INSERT INTO chartdata(year,probe1, probe5) VALUES (%s, %s, %s)",(year, temp, probe5))
        return redirect(url_for('register'))

    return render_template('input.html',data=data)

app.secret_key="jyooGbO0eXelz9lrRQH6f0FL4r57SRM8"
if __name__ == '__main__':

    app.run(debug=True)
