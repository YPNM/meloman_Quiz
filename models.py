from app import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    __tablename__ = "user"
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    superadmin = db.Column(db.Boolean, nullable=False, default=0)
    city_id = db.Column(db.BINARY(16))
    city_superadmin = db.Column(db.Boolean, default=0)
    pwd = db.Column(db.String(300), nullable=False, unique=True)

    def __repr__(self):
        return '<User %r>' % self.username