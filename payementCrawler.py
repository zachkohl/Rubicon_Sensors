from flask import Flask
from flask_sqlalchemy import SQLAlchemy




app = Flask(__name__) #Starts the flask application, passes into other stuff. Used to tie the whole website framework together

#from app import db

####################################################DATABASE CONNECTIONS###############################################################
#Just comment out the parts parts you aren't using and remove the comments for the machine you are using. Should work fine.

with open('static/databaseURI.txt','r') as file: #See https://docs.python.org/3/library/functions.html#open
    databaseURI=file.read()
app.config['SQLALCHEMY_DATABASE_URI'] = databaseURI
    

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
db = SQLAlchemy(app)

#from app import db
from dbModels import *
print('hello world!')
x = sensors.query.first()

print(x)


