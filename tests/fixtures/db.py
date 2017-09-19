import sqlalchemy
from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, DateTime
from sqlalchemy.ext.declarative import declarative_base

engine = sqlalchemy.create_engine('sqlite://')

Base = declarative_base()

class Patient(Base):
    __tablename__ = 'patient'

    id = Column(Integer, primary_key=True)
    mrn = Column(String)
    name = Column(String)
    age = Column(Integer)

class Lab(Base):
    __tablename__ = 'lab'
    id = Column(Integer, primary_key=True)
    patient_mrn = Column(String)
    name = Column(String)
    value = Column(Numeric)
    order_time = Column(DateTime)
    taken_time = Column(DateTime)
