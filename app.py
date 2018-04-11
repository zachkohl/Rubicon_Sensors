from flask import Flask, render_template, request, url_for, redirect, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user #,UserMixin #now comes from dbModels
from wtforms import Form, BooleanField, StringField, validators,PasswordField
from werkzeug.security import check_password_hash, generate_password_hash #don't know why this works, have not installed in virtualdev
from wtforms import Form, BooleanField, StringField, validators,PasswordField
from flask.ext.bcrypt import Bcrypt, generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import stripe 
#import gviz_api #google chart api
from flask_sslify import SSLify #force HTTPS
from flask_httpauth import HTTPBasicAuth #Import httpAuth for android login
import json
import time
import datetime
#import requests #for Particle customer creation
#from requests_oauthlib import OAuth2Session #See https://requests-oauthlib.readthedocs.io/en/latest/examples/real_world_example.html




app = Flask(__name__) #Starts the flask application, passes into other stuff. Used to tie the whole website framework together
bcrypt = Bcrypt(app) #use for encryption


####################################################DATABASE CONNECTIONS###############################################################
#Just comment out the parts parts you aren't using and remove the comments for the machine you are using. Should work fine.
# if __name__ == '__main__':
#     with open('static/databaseURI.txt','r') as file: #See https://docs.python.org/3/library/functions.html#open
#         databaseURI=file.read()
#     app.config['SQLALCHEMY_DATABASE_URI'] = databaseURI
    
# else:
#     sslify = SSLify(app) #Runs SSLify, need this in production to force use of SSL. Don't care in development.
#     SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(

#         username="rubiconsensors",
#         password="wf5PWRM4",
#         hostname="rubiconsensors.mysql.pythonanywhere-services.com",
#         databasename="rubiconsensors$riversensedb",
#     )


#     app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
#     app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
#     app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# db = SQLAlchemy(app)
###FOR USE WITH RECREATING DATABASE
with open('static/databaseURI.txt','r') as file: #See https://docs.python.org/3/library/functions.html#open
    databaseURI=file.read()
app.config['SQLALCHEMY_DATABASE_URI'] = databaseURI
db = SQLAlchemy(app)






# ########################################FLASK-SQLALCHEMY DATABASE MODELS########################################################
#Many to many relationship tables. See https://www.youtube.com/watch?v=OvhoYbjtiKc
views = db.Table('views',
    db.Column('sensors_id',db.Integer,db.ForeignKey('sensors.id'), primary_key=True),
    db.Column('user_id',db.Integer,db.ForeignKey('users.id'),primary_key=True)
)

owners = db.Table('owners',
    db.Column('sensors_id',db.Integer,db.ForeignKey('sensors.id'), primary_key=True, unique=True),
    db.Column('user_id',db.Integer,db.ForeignKey('users.id'),primary_key=True)
)
    #Create a model of the database for use in python
class Data(db.Model): #The name is the name from the SQL database. This is not about setting up a SQL database!
                               #It is about creating a local model of the far away SQL database
                               #We pass in db.model because that will turn the class into something that SQLAlchemy can use SPECIAL TO FLASK SQLALCHEMY
                               #Recall  db = SQLAlchemy(app)
    id = db.Column('id', db.Integer, primary_key=True) #Describes the first column.
                                                                #Input arguments are the column name, what the datatype is, and if it is a primary key
                                                                #Don't have to worry about auto imcrement normally because SQL does that automatically. See http://docs.sqlalchemy.org/en/latest/core/metadata.html#sqlalchemy.schema.Column.params.onupdate
    sensors = db.Column('sensors', db.Integer,db.ForeignKey('sensors.id'))
    ISO8601 = db.Column('ISO8601', db.String(80))                   #descriptions of the other columns, for explanation of legal data types, see https://dev.mysql.com/doc/refman/5.7/en/numeric-types.html
                                                                #Recall also that this is flask-SQLAlchemy, so google the docs for more info.
    data = db.Column('data', db.Integer)
    timestamp = db.Column('timestamp', db.String(80))
    installation = db.Column('installation', db.Integer) #Describes the first column.

    #We now have a map for SQLAlchemy to use to relate tot the database. This will let us do all the fun SQLAlchemy commands to electron1
    # or whatever we name it. Things like data.query.all() See functions for use examples.





#USERS table, very special. Note the UserMixin getting passed in.
class users(UserMixin, db.Model):
     #See https://www.pythoncentral.io/introductory-tutorial-python-sqlalchemy/
    id = db.Column(db.Integer, primary_key=True)

    owners = db.relationship('sensors',secondary=owners,lazy=True, backref= db.backref('owner', lazy=True))
    viewers = db.relationship('sensors',secondary=views,lazy=True,
        backref=db.backref('viewers', lazy=True))
    username = db.Column(db.String(80), unique=True) #https://www.w3schools.com/sql/sql_foreignkey.asp
                                                                                     #FORIEGN KEY
                                                                                     #-The foriegn key is the column that can have more than
                                                                                     #-one entry of the same type.
                                                                                     #-The primary key (same numbers), sits in the other
                                                                                     #-table and is unique to each row. It is the PRIMARY KEY.
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    stripeID = db.Column(db.String(120))
    subscriptionNumber = db.Column(db.Integer)
    

    def __init__(self, username, email,password):
        self.username = username
        self.email = email
        self.password = password

    def __repr__(self):
        return '<User %r>' % self.username

class sensors(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    particleID = db.Column(db.String(80), unique=True)
    location = db.Column(db.String(120))
    imei =db.Column(db.String(120))
    iccid =db.Column(db.String(80))
    Data = db.relationship('Data',backref= db.backref('sensorID', lazy=True))
    rubiconID = db.Column(db.String(80), unique=True)
    SensorType = db.relationship('sensorType',backref= db.backref('sensorID', lazy=True))
    creationDate = db.Column(db.DateTime)
    notDeployed = db.Column(db.Boolean)
    payementDay = db.Column(db.Integer)
    proRate = db.Column(db.Float)
    PayedFlag = db.Column(db.Boolean)
    statusCode = db.relationship('statusCode',backref= db.backref('sensorID', lazy=True)) 
    notes = db.Column('notes', db.Text)
    installation = db.Column(db.Integer)
    #deletionDate = db.Column(db.DateTime) #ADD THIS!!


class sensorType(db.Model): 
    id = db.Column('id', db.Integer, primary_key=True) 
    sensors = db.Column('sensors', db.Integer,db.ForeignKey('sensors.id'))
    sensorTypeName = db.Column('sensorTypeName', db.String(80))                  
    aboutSensorType = db.Column('aboutSensorType', db.Text)
    monthlyCost = db.Column('monthlyCost', db.Float)

class statusCode(db.Model): 
    id = db.Column('id', db.Integer, primary_key=True) 
    sensors = db.Column('sensors', db.Integer,db.ForeignKey('sensors.id'))
    statusCodeName = db.Column('statusCodeName', db.String(80))                  
    aboutStatusCode = db.Column('aboutStatusCode', db.Text)


class activationDate(db.Model): 
    id = db.Column('id', db.Integer, primary_key=True) 
    sensors = db.Column('sensors', db.Integer,db.ForeignKey('sensors.id'))
    activation_Date = db.Column(db.DateTime)
    installation = db.Column(db.Integer)







###################################################LOGIN STUFF######################################################
#See https://blog.pythonanywhere.com/158/

#Step 1, make sure secrete key is inplace, ours is at the bottom of this document

login_manager = LoginManager() #Create an instance of Flask-Login
login_manager.init_app(app) #Associate the instance with the fask app

#These are forms that are used later. use tools from wtforms
class RegistrationForm(Form):
    username     = StringField('Username', [validators.Length(min=4, max=25),validators.Required()])
    password     = PasswordField('Password', [validators.Length(min=4, max=25),validators.Required()])
    email        = StringField('Email', [validators.Length(min=4, max=100),validators.Required()])

class LoginForm(Form):
    username     = StringField('Username', [validators.Required()])
    password     = PasswordField('Password', [validators.Required()])

#Create user class that will tell us something about the user. This is not the database model. This is the individual that logs in

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
                return redirect(url_for('sensorlist'))
            else:
                #flash('password failed')
                return redirect(url_for('login'))


        else:
            return redirect(url_for('login'))

    return render_template('login.html', form=form)

#The register function is very similar to login. But it stores into a database rather than doing a query.
@app.route('/register.html', methods = [ "GET", "POST"])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST'and form.validate():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        pw_hash = bcrypt.generate_password_hash(password)
  
        
        db.engine.execute("INSERT INTO users(username,password,email) VALUES (%s, %s,%s)",(username, pw_hash,email))
        
        



        flash('new user created')
        return redirect(url_for('home'))
    return render_template('register.html', form= form)


@app.route('/logout.html')
#This is pretty simple, we just call the library included logout_user()
def logout():
    logout_user()
    return render_template('logout.html')

###################################################HOME PAGE##################################################


@app.route('/')
def home():
    return render_template('home.html')

##################################################SENSOR REGISTER################################################


class sensorRegisterForm(Form):
    rubiconID     = StringField('rubiconID', [validators.Length(max=80),validators.Required()])
    location     = StringField('location', [validators.Length(max=120),validators.Required()])

##################################################ADMIN SENSOR REGISTER################################################


class adminSensorRegisterForm(Form):
    particleID = StringField('particleID', [validators.Length(max=80),validators.Required()])
    rubiconID     = StringField('rubiconID', [validators.Length(max=80),validators.Required()])
    iccid     = StringField('iccid', [validators.Length(max=80),validators.Required()])

@app.route('/adminNewSensor.html', methods = [ "GET", "POST"])
@login_required
def adminNewSensor():
    if not current_user.username == 'admin':
        return redirect(url_for('home'))
    #Regular function stuff
    form =adminSensorRegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        particleID = form.particleID.data
        rubiconID =form.rubiconID.data
        iccid =form.iccid.data
        ST = sensorType(sensorTypeName = "RiverSense_1",aboutSensorType="This is the first iteration sensor we are working on, circa April 2018.",monthlyCost=4)

        adminSensor = sensors(particleID = particleID,location='notDeployed',imei='notSet',iccid=iccid,rubiconID=rubiconID,SensorType=[ST],creationDate=time.strftime('%Y-%m-%d %H:%M:%S'),notDeployed =True,installation=0)
        db.session.add(adminSensor)
        db.session.commit()

        flash('sensor added and is ready for registration by users')
        return render_template('adminNewSensor.html',form = form)
    return render_template('adminNewSensor.html',form = form)


@app.route('/newSensor.html', methods = [ "GET", "POST"])
@login_required
def newSensor():
    if current_user.stripeID is None:
        return redirect(url_for('payment'))
    if request.method == 'POST':
        rubiconID = request.form['rubiconID']
        location = request.form['location']
        if not request.form.getlist('choice'):
            flash('please agree to terms of service')
            return redirect(url_for('newSensor'))            
        if location == '':
            flash('please fill in a name')
            return redirect(url_for('newSensor'))
        checkName =  db.engine.execute("SELECT id FROM SENSORS JOIN OWNERS ON SENSORS.id = OWNERS.sensors_id WHERE OWNERS.user_id = %s AND SENSORS.location = %s",(current_user.id,location))
        array_data = []
        for items in checkName:
            array_data.append(items.id)
        print('1')
        print(array_data)
        if  array_data ==[]:
            newSensor = sensors.query.filter_by(rubiconID = rubiconID).first() #Do a database query of rubiconID
            if newSensor:
                if newSensor.notDeployed == True:
                    newSensor.notDeployed = False
                    newSensor.installation = newSensor.installation + 1
                    current_user.owners.append(newSensor) #claim ownership
                    newSensor.location = location
                    activation_Date = activationDate(sensors = newSensor.id,activation_Date = time.strftime('%Y-%m-%d %H:%M:%S') )
                    current_user.subscriptionNumber += 1
                    db.session.add(activation_Date)
                    db.session.add(newSensor)
                    db.session.add(current_user)
                    subscription = stripe.Subscription.create(
                    customer=current_user.stripeID,
                    items=[
                    {
                    'plan': '988931021243392',
                    'quantity': current_user.subscriptionNumber,
                    },
                    ],
                    )
                    db.session.commit() #Commit it
                    flash('Sensor ' + newSensor.location + " successfully registered" )
                    return redirect(url_for('sensorlist'))
                else:
                    flash('Invalid rubicon ID')
                    return redirect(url_for('newSensor'))
            else:
                flash('Invalid rubicon ID')
                return redirect(url_for('newSensor'))
        else:
            flash('You already have a sensor by that name')
        return redirect(url_for('newSensor'))
    
    return render_template('newSensor.html')
###############################################DELETE SENSOR#####################################################
@app.route('/deleteSensor.html', methods = [ "GET", "POST"])
@login_required
def deleteSensor():
    form = sensorRegisterForm(request.form)
    if request.method == 'POST':
        rubiconID = form.rubiconID.data
        location =form.location.data

        oldSensor = sensors.query.filter_by(rubiconID = rubiconID).first() #Do a database query of the username
     

        if oldSensor:
            #If the user object got created by the database, then do this stuff
            if oldSensor.owner[0] == current_user:
                oldSensor.notDeployed = True
                oldSensor.deletionDate = datetime.datetime.now()
                  
                db.engine.execute("DELETE FROM owners WHERE sensors_id =%s",(oldSensor.id))
                db.engine.execute("DELETE FROM views WHERE sensors_id =%s",(oldSensor.id))
                
                current_user.subscriptionNumber = current_user.subscriptionNumber - 1
                customer = stripe.Customer.retrieve(current_user.stripeID, expand=['subscriptions'])
                subscription = customer.subscriptions.data
                obj = subscription[0]
                obj2 =obj.id

                if current_user.subscriptionNumber == 0:
                    customer = stripe.Customer.retrieve(current_user.stripeID)
                    subscription = stripe.Subscription.retrieve(obj2)
                    subscription.delete()
                else:
                    subscription = stripe.Subscription.create(
                    customer=current_user.stripeID,
                    items=[
                    {
                    'plan': '988931021243392',
                    'quantity': current_user.subscriptionNumber,
                    },
                    ],
                    )
                db.session.commit()
                flash('Sensor deleted')
                
                return redirect(url_for('sensorlist'))
            else:
                flash('sensor not found')
                return redirect(url_for('deleteSensor'))
        else:
            flash('invalid registration code')
            return redirect(url_for('deleteSensor'))
        return redirect(url_for('deleteSensor'))
    return render_template('deleteSensor.html', form= form)
################################################  LIST OF SENSORS       ##########################################
@app.route('/sensors.html')
def sensorlist():
    myListOfSensors = current_user.owners
    
    return render_template('sensors.html',sensors=myListOfSensors)

################################################DISPLAY SENSOR DATA###################################################

@app.route('/<location>.html') #Variables can be included in the route. See http://flask.pocoo.org/docs/0.12/quickstart/#routing
#@login_required #This makes this page require the user to be logged in to see it.
def dashboard(location):
    if not current_user.is_authenticated:
        return login_manager.unauthorized()
    else: #logic to make sure user owns this sensor
        listOfSensors = current_user.owners
        myLocations = [] #One has to do a for loop to get stuff out of a query. Do it here or do it in the template. This time we chose template.
        for items in listOfSensors: #Iteration will cycle through each row
            myLocations.append(items.location)
        if not location in myLocations:
            return redirect(url_for('sensorlist'))


    selectedSensor = sensors.query.filter_by(location = location).first()
    sensorID = selectedSensor.id
    installation =selectedSensor.installation

    chartdata = Data.query.filter_by(sensors =sensorID, installation=installation)
    selectedSensorID = selectedSensor.id
    sensorLocation =selectedSensor.location
            #Google charts tooka lot of work. Here are notes
            #See http://banjolanddesign.com/flask-google-charts.html
            # See https://www.codementor.io/sheena/understanding-sqlalchemy-cheat-sheet-du107lawl
            # See https://www.youtube.com/watch?v=Tu4vRU4lt6k
            #http://flask-sqlalchemy.pocoo.org/2.3/quickstart/
    #chartdata = pipe_sensor.query.all() #This returns a lists of dictionaries. Each item in the list is a dictionary (dictionary = key-value pair)
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



    return render_template('dashboard.html',array_ISO8601=array_ISO8601,data=array_data,selectedSensorID=selectedSensorID,sensorLocation=sensorLocation) #Pass arrays containing columns to the javascript


############################################################# INPUT #######################################################################################

@app.route('/input.html', methods = ['GET', 'POST']) #This function is for the particle webhook
def particle():

    if request.method == 'POST':
        webhook = request.form   #see http://flask.pocoo.org/docs/0.12/api/#flask.Request
        data = webhook['data']   #look inside the multidict
        ISO8601 = webhook['published_at']
        particleID =webhook['coreid']
        selectedSensor = sensors.query.filter_by(particleID = particleID).first()
        selectedSensorID = selectedSensor.id
        installationNumber = selectedSensor.installation
        if selectedSensor.notDeployed == False:
            db.engine.execute("INSERT INTO data(sensors,ISO8601,data,installation) VALUES (%s, %s, %s, %s)",(selectedSensorID,ISO8601, data,installationNumber))
        # id | sensors | ISO8601 | data | timestamp
        #newDataPoint = data(sensors=selectedSensorID,ISO8601=ISO8601,data=data)
        #db.session.add(newDataPoint) #Add the new object to the que

        #selectedSensor.data.append(newDataPoint)
        #db.session.commit()

        return redirect(url_for('register'))

    return redirect(url_for('deleteSensor'))
############################################################################### TEST DATA #########################################################################
@app.route('/testData.html') #This function is for the particle webhook
def testData():
    if __name__ == '__main__':
    #TEST DATA 1
        data = 1  
        ISO8601 = '2018-04-07T00:02:31.826Z'
        particleID ="200041001647373037383634"
        selectedSensor = sensors.query.filter_by(particleID = particleID).first()
        selectedSensorID = selectedSensor.id
        installationNumber = selectedSensor.installation
        if selectedSensor.notDeployed == False:
            db.engine.execute("INSERT INTO data(sensors,ISO8601,data,installation) VALUES (%s, %s, %s, %s)",(selectedSensorID,ISO8601, data,installationNumber))
    
    #TEST DATA 2
        data = 10  
        ISO8601 = '2018-04-07T00:03:31.826Z'
        particleID ="200041001647373037383634"
        selectedSensor = sensors.query.filter_by(particleID = particleID).first()
        selectedSensorID = selectedSensor.id
        installationNumber = selectedSensor.installation
        if selectedSensor.notDeployed == False:
            db.engine.execute("INSERT INTO data(sensors,ISO8601,data,installation) VALUES (%s, %s, %s, %s)",(selectedSensorID,ISO8601, data,installationNumber))
    
    #TEST DATA 3
        data = 5  
        ISO8601 = '2018-04-07T00:04:31.826Z'
        particleID ="200041001647373037383634"
        selectedSensor = sensors.query.filter_by(particleID = particleID).first()
        selectedSensorID = selectedSensor.id
        installationNumber = selectedSensor.installation
        if selectedSensor.notDeployed == False:
            db.engine.execute("INSERT INTO data(sensors,ISO8601,data,installation) VALUES (%s, %s, %s, %s)",(selectedSensorID,ISO8601, data,installationNumber))
        
        return 'Data inputed correctly'
    else:
        return render_template('input.html') 

############################################Stripe Stuff#############################################################
with open('static/stripeSecretKey.txt','r') as file: #See https://docs.python.org/3/library/functions.html#open
    stripe.api_key=file.read()
stripe.api_version = '2018-02-28'

################################################# STRIPE PAYEMENT #########################################################################################

@app.route('/payment.html')
def payment():

    return render_template('payment.html')

@app.route('/charge', methods = ['POST'])
def charge():
    token = request.form['stripeToken'] 
    customer = stripe.Customer.create(
    source=token,
    email=current_user.email
    )
    current_user.stripeID = customer.id
    current_user.subscriptionID = 0
    db.session.commit()

    subscription = stripe.Subscription.create(
    customer=current_user.stripeID,
    items=[{'plan': '988931021243392'}],
            )
    return render_template('charge.html')

@app.route('/privacypolicy')
def privacypolicy():

    return render_template('privacypolicy.html')

@app.route('/termsofservice')
def termsofservice():

    return render_template('termsofservice.html')


###################################           ANDROID APP                   #####################################

#See the docs at https://flask-httpauth.readthedocs.io/en/latest/

auth = HTTPBasicAuth()

@auth.verify_password #https://github.com/miguelgrinberg/Flask-HTTPAuth/blob/master/examples/basic_auth.py
def verify_password(username,password):
    user = users.query.filter_by(username = username).first() #Do a database query of the username
    if user:
        #If the user object got created by the database, then do this stuff
            return check_password_hash( user.password, password)
    else:
        return False
    return False

@app.route('/api')
@auth.login_required
def index():
    selectedSensor = sensors.query.filter_by(location = dashboard).first()
    chartdata = selectedSensor.Data



    array_ISO8601 = []
    for items in chartdata:
        array_ISO8601.append(items.ISO8601)
    array_data = []
    for items in chartdata:
        array_data.append(float(items.data))


        apiData = json.dumps(dict(zip(array_ISO8601,array_data)))
    #return "Hello, %s!" % auth.username()
    return apiData


###################################################JAVASCRIPT GAMES##################################################


@app.route('/javascriptGames')
def javascriptGames():
    return render_template('javascriptGames/javascriptGames.html')







app.secret_key="jyooGbO0eXelz9lrRQH6f0FL4r57SRM8"
if __name__ == '__main__':

    app.run(debug=True) #,ssl_context="adhoc"










