from sqlalchemy import Column, ForeignKey, ForeignKeyConstraint, Index, Integer, String, Table
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()
metadata = Base.metadata


class Flowsensor(Base):
    __tablename__ = 'flowsensor'

    idFlowSensor = Column(Integer, primary_key=True, nullable=False)
    Payer_PayerID = Column(ForeignKey('payer.PayerID'), primary_key=True, nullable=False, index=True)
    Address = Column(String(100))

    payer = relationship('Payer')
    viewer = relationship('Viewer', secondary='viewer_has_flowsensor')


class Flowsensordatum(Base):
    __tablename__ = 'flowsensordata'

    idFlowSensor = Column(Integer, primary_key=True, nullable=False)
    ISO8601 = Column(String(100))
    Data = Column(Integer)
    FlowSensor_idFlowSensor = Column(ForeignKey('flowsensor.idFlowSensor'), primary_key=True, nullable=False, index=True)

    flowsensor = relationship('Flowsensor')


class Payer(Base):
    __tablename__ = 'payer'

    PayerID = Column(Integer, primary_key=True, unique=True)
    UserName = Column(String(45))
    Email = Column(String(90))
    FirstName = Column(String(45))
    LastName = Column(String(45))
    Password = Column(String(100))
    register_date = Column(String(100))


class User(Base):
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

    payer = relationship('Payer')
    viewer = relationship('Viewer')


class Viewer(Base):
    __tablename__ = 'viewer'

    idViewer = Column(Integer, primary_key=True, nullable=False)
    PayerID = Column(Integer)
    Login = Column(String(45))
    FirstName = Column(String(45))
    LastName = Column(String(45))
    Email = Column(String(90))
    Payer_PayerID = Column(ForeignKey('payer.PayerID'), primary_key=True, nullable=False, index=True)

    payer = relationship('Payer')


t_viewer_has_flowsensor = Table(
    'viewer_has_flowsensor', metadata,
    Column('Viewer_idViewer', ForeignKey('viewer.idViewer'), primary_key=True, nullable=False, index=True),
    Column('FlowSensor_idFlowSensor', ForeignKey('flowsensor.idFlowSensor'), primary_key=True, nullable=False, index=True)
)