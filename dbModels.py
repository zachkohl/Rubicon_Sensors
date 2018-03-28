#from flask import Flask, render_template, request, url_for, redirect, flash, jsonify
#from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
#from app import UserMixin
#from app import app
from payementCrawler import db

########################################FLASK-SQLALCHEMY DATABASE MODELS########################################################
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
