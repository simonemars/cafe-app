from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime

app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:5174", "http://localhost:5175", "http://localhost:5176"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafe.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    rating = db.Column(db.Float, default=0.0)
    image_url = db.Column(db.String(200))
    open_hours = db.Column(db.String(100))
    available_tables = db.Column(db.Integer, default=0)
    distance = db.Column(db.String(50))

class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    cafe_id = db.Column(db.Integer, db.ForeignKey('cafe.id'), nullable=False)
    date_time = db.Column(db.DateTime, nullable=False)
    number_of_guests = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='confirmed')

# Initialize database with sample data
def init_db():
    with app.app_context():
        # Drop all tables and recreate them
        db.drop_all()
        db.create_all()
        
        # Add sample cafes
        cafes = [
            Cafe(
                name='Fairgrounds Coffee and Tea',
                address='5500 S. University Ave',
                description='A cozy cafe with a great selection of coffee and tea',
                rating=4.7,
                image_url='https://images.unsplash.com/photo-1445116572660-236099ec97a0?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80',
                open_hours='7:00 AM - 7:00 PM',
                available_tables=4,
                distance='0.5 km'
            ),
            Cafe(
                name='Hallowed Grounds',
                address='1234 W. 57th St',
                description='A popular spot for students and locals',
                rating=4.9,
                image_url='https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80',
                open_hours='6:30 AM - 8:30 PM',
                available_tables=6,
                distance='1.2 km'
            ),
            Cafe(
                name='Plein Air Cafe',
                address='5751 S. Ellis Ave',
                description='A charming cafe with outdoor seating',
                rating=4.5,
                image_url='https://images.unsplash.com/photo-1511920170033-f8396924c348?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80',
                open_hours='6:00 AM - 9:00 PM',
                available_tables=3,
                distance='0.8 km'
            )
        ]
        
        for cafe in cafes:
            db.session.add(cafe)
        
        db.session.commit()

# Routes
@app.route('/api/cafes', methods=['GET'])
def get_cafes():
    cafes = Cafe.query.all()
    return jsonify([{
        'id': cafe.id,
        'name': cafe.name,
        'address': cafe.address,
        'description': cafe.description,
        'rating': cafe.rating,
        'image_url': cafe.image_url,
        'open_hours': cafe.open_hours,
        'available_tables': cafe.available_tables,
        'distance': cafe.distance
    } for cafe in cafes])

@app.route('/api/cafes/<int:cafe_id>', methods=['GET'])
def get_cafe(cafe_id):
    cafe = Cafe.query.get_or_404(cafe_id)
    return jsonify({
        'id': cafe.id,
        'name': cafe.name,
        'address': cafe.address,
        'description': cafe.description,
        'rating': cafe.rating,
        'image_url': cafe.image_url,
        'open_hours': cafe.open_hours,
        'available_tables': cafe.available_tables,
        'distance': cafe.distance
    })

@app.route('/api/reservations', methods=['POST'])
def create_reservation():
    data = request.get_json()
    reservation = Reservation(
        user_id=data['user_id'],
        cafe_id=data['cafe_id'],
        date_time=datetime.fromisoformat(data['date_time']),
        number_of_guests=data['number_of_guests']
    )
    db.session.add(reservation)
    db.session.commit()
    return jsonify({'message': 'Reservation created successfully'}), 201

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000) 