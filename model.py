from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class TeachersLogin(db.Model):
  __tablename__ = 'TeachersLogin'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.Text, nullable=False)
  email = db.Column(db.Text, unique=True, nullable=False)
  password = db.Column(db.Text, nullable=False)
  classes = db.Column(db.JSON, nullable=False)
  ip = db.Column(db.JSON)
  role = db.Column(db.Text, nullable=False)
