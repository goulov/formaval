import os, csv, datetime
import sqlalchemy as db
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from parameters import dbpath, paths2csv

Base = declarative_base()

class student(Base):
    __tablename__ = "students"
    _id = db.Column("id", db.Integer, primary_key=True)
    istid = db.Column(db.String(10))
    course = db.Column(db.String(20))
    version = db.Column(db.String(30))
    shift = db.Column(db.String(20))
    timelogged1st = db.Column(db.DateTime)
    iplogged1st = db.Column(db.String(15))

class logs(Base):
    __tablename__ = "logs"
    _id = db.Column("id", db.Integer, primary_key=True)
    time = db.Column(db.DateTime)
    req = db.Column(db.String(100))
    status = db.Column(db.String(100))
    ip = db.Column(db.String(15))
    repeatedQ = db.Column(db.Boolean)

def create(session, paths):
    for filecsv in paths:
        with open(filecsv) as f:
            reader = csv.DictReader(f, delimiter=",")
            for row in reader:
                istid = row["Username"]
                shift = row["Turno Problemas"]
                course = filecsv.split('_')[0] # grab course from filename
                if shift:
                    session.add(student(istid=istid, shift=shift, course=course))
                else: # student is not signed up for a shift
                    session.add(student(istid=istid, course=course))
        session.commit()

if __name__ == '__main__':
    assert not os.path.isfile(dbpath), "database already exists"

    engine = db.create_engine("sqlite:///"+dbpath, echo=True)
    Base.metadata.create_all(engine)
    DBSession = sessionmaker(bind=engine)
    session = DBSession()

    create(session, paths2csv)
