from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    trips = db.relationship('Trip', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'created_at': self.created_at.isoformat()
        }


class Trip(db.Model):
    __tablename__ = 'trips'

    trip_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    source = db.Column(db.String(100), nullable=False, default='')
    destination = db.Column(db.String(100), nullable=False)
    days = db.Column(db.Integer, nullable=False)
    budget = db.Column(db.Float, nullable=False)
    travelers = db.Column(db.Integer, default=1)
    interests = db.Column(db.String(500), nullable=False)
    travel_dates = db.Column(db.String(100), nullable=True)
    itinerary = db.Column(db.Text, nullable=False)
    weather_data = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'trip_id': self.trip_id,
            'user_id': self.user_id,
            'source': self.source,
            'destination': self.destination,
            'days': self.days,
            'budget': self.budget,
            'travelers': self.travelers,
            'interests': self.interests,
            'travel_dates': self.travel_dates,
            'itinerary': self.itinerary,
            'weather_data': self.weather_data,
            'created_at': self.created_at.isoformat()
        }
