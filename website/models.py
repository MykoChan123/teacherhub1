from website import db
from sqlalchemy import func
from datetime import datetime


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), nullable=False)
    fname = db.Column(db.String(150), nullable=False)
    lname = db.Column(db.String(150), nullable=False)
    password = db.Column(db.String(2000), nullable=False)
    position = db.Column(db.String(50), nullable=False)
    advisory = db.Column(db.String(50), nullable=False)
    img = db.Column(db.String(2000), nullable=True)
    mblimit = db.Column(db.String(1000000), nullable=True)
    status = db.Column(db.String(10), nullable=True)
    valid_id = db.Column(db.String(1000), nullable=True)


class Announcement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.String(1000), nullable=False)
    date_created = db.Column(db.DateTime, default=lambda: datetime.now().replace(microsecond=0), nullable=False)
    user__id = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), nullable=False)
    fullname = db.Column(db.String(100), nullable=False)


class Folders(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    folder_name = db.Column(db.String(200),nullable=False)
    folder_path = db.Column(db.String(200), nullable=False)
    folder_user = db.Column(db.Integer, nullable=False)
    fname = db.Column(db.String(200), nullable=False)
    lname = db.Column(db.String(200), nullable=False)
    date = db.Column(db.DateTime, default=lambda: datetime.now().replace(microsecond=0), nullable=False)
    password = db.Column(db.String(10), nullable=True)

class Files(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(200), nullable=False)
    file_path = db.Column(db.String(200), nullable=False)
    file_user = db.Column(db.Integer(), nullable=False)
    folderid = db.Column(db.Integer(), nullable=False)
    lname = db.Column(db.String(200), nullable=False)
    fname = db.Column(db.String(200), nullable=False)
    date = db.Column(db.DateTime, default=lambda: datetime.now().replace(microsecond=0), nullable=False)
    position = db.Column(db.String(255), nullable=False)
    size = db.Column(db.String(10000000), nullable=True)

class Chat(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    msg = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.String(200), nullable=False)
    date = db.Column(db.DateTime, default=datetime.now, nullable=False)
    user_email = db.Column(db.String(200), nullable=False)


class Pm(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    msg = db.Column(db.String(250), nullable=False)
    fr = db.Column(db.Integer(), nullable=False)
    to = db.Column(db.Integer(), nullable=False)
    date = db.Column(db.DateTime, default=lambda: datetime.now().replace(microsecond=0), nullable=False)
    fname = db.Column(db.String(255), nullable=False)
    lname = db.Column(db.String(255), nullable=False)
    position = db.Column(db.String(255), nullable=False)



class Loginlog(db.Model):
    id = db.Column(db.Integer(), primary_key=True, nullable=False)
    userid = db.Column(db.Integer(), nullable=False)
    fname = db.Column(db.String(200), nullable=False)
    lname = db.Column(db.String(200), nullable=False)
    date = db.Column(db.DateTime, default=lambda: datetime.now().replace(microsecond=0), nullable=False)

class Signoutlog(db.Model):
    id = db.Column(db.Integer(), primary_key=True, nullable=False)
    userid = db.Column(db.Integer(), nullable=False)
    fname = db.Column(db.String(200), nullable=False)
    lname = db.Column(db.String(200), nullable=False)
    date = db.Column(db.DateTime, default=lambda: datetime.now().replace(microsecond=0), nullable=False)

class Loginfailedlog(db.Model):
    id = db.Column(db.Integer(), primary_key=True, nullable=False)
    email = db.Column(db.String(200), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    date = db.Column(db.DateTime, default=lambda: datetime.now().replace(microsecond=0), nullable=False)


class Website(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(200), nullable=True)
    logo = db.Column(db.String(200), nullable=True) 


class Useractivity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(200), nullable=False)
    date = db.Column(db.DateTime, default=lambda: datetime.now().replace(microsecond=0), nullable=False)

class Position(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=True)

class Advisory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=True)

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(200), nullable=True)
    password = db.Column(db.String(200), nullable=True)


