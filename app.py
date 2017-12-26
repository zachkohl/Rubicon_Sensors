from flask import Flask, render_template, request, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from wtforms import Form, BooleanField, StringField, validators,PasswordField
from flask.ext.bcrypt import Bcrypt, generate_password_hash, check_password_hash
#from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import gviz_api #google chart api






app = Flask(__name__)


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


if __name__ == '__main__':
    app.secret_key="jyooGbO0eXelz9lrRQH6f0FL4r57SRM8"
    app.run(debug=True)
