"""
init_db.py — Initialize the WanderAI database with sample data.
Run once: python init_db.py
"""
import os
import sys
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
os.makedirs('database', exist_ok=True)

from app import app, db
from models.models import User, Trip

SAMPLE_ITINERARY = json.dumps({
    "overview": "Paris, the City of Light, captivates visitors with its timeless architecture, world-class cuisine, and unparalleled art scene. From the iconic Eiffel Tower to hidden neighbourhood cafés, every corner tells a story.",
    "budget_breakdown": {
        "accommodation": 600, "food": 400, "transportation": 200,
        "activities": 200, "miscellaneous": 100, "total": 1500
    },
    "travel_tips": [
        "Buy a Paris Visite transport pass for unlimited metro/bus travel.",
        "Book Louvre and Musée d'Orsay tickets online to skip queues.",
        "Most museums are free on the first Sunday of each month.",
        "Carry an umbrella — Paris weather is unpredictable year-round.",
        "Tipping is not compulsory but rounding up the bill is appreciated."
    ],
    "days": [
        {
            "day": 1, "title": "Day 1: Arrival & Eiffel Tower",
            "morning": "Arrive at CDG airport and check in to your hotel near the city centre. Freshen up and have a classic Parisian breakfast at a nearby café.",
            "afternoon": "Head to the Champ de Mars and visit the Eiffel Tower. Explore the surrounding neighbourhood and the Trocadéro gardens.",
            "evening": "Stroll along the Seine riverbanks. Dine at a traditional brasserie in Saint-Germain-des-Prés.",
            "meals": {"breakfast": "Croissants & café au lait at a local boulangerie", "lunch": "Crêperie near the Eiffel Tower (~$15)", "dinner": "Brasserie Lipp, Saint-Germain (~$40)"},
            "highlights": ["Eiffel Tower", "Champ de Mars", "Trocadéro", "Seine riverbanks"],
            "daily_cost": 300
        },
        {
            "day": 2, "title": "Day 2: Louvre & Le Marais",
            "morning": "Spend the morning at the Louvre Museum — pre-book tickets. Focus on the Mona Lisa, Venus de Milo, and the Egyptian antiquities.",
            "afternoon": "Walk through the Tuileries Garden then explore Le Marais district — visit Place des Vosges and the Picasso Museum.",
            "evening": "Dinner in Le Marais — try falafel at L'As du Fallafel or a modern bistro.",
            "meals": {"breakfast": "Café near the Louvre", "lunch": "Café Marly overlooking the Louvre (~$25)", "dinner": "L'As du Fallafel, Le Marais (~$12)"},
            "highlights": ["Louvre Museum", "Tuileries Garden", "Place des Vosges", "Picasso Museum"],
            "daily_cost": 280
        },
        {
            "day": 3, "title": "Day 3: Montmartre & Sacré-Cœur",
            "morning": "Explore the bohemian neighbourhood of Montmartre. Visit Sacré-Cœur Basilica and enjoy panoramic views of Paris.",
            "afternoon": "Browse the artist studios around Place du Tertre. Visit the Moulin Rouge area for photographs.",
            "evening": "Wine and cheese at a wine bar in Pigalle, then a cabaret show if budget allows.",
            "meals": {"breakfast": "Traditional breakfast at a Montmartre café", "lunch": "Lunch at a neighbourhood bistro (~$20)", "dinner": "Wine bar dinner in Pigalle (~$35)"},
            "highlights": ["Sacré-Cœur", "Place du Tertre", "Moulin Rouge", "Montmartre vineyards"],
            "daily_cost": 250
        },
        {
            "day": 4, "title": "Day 4: Versailles Day Trip",
            "morning": "Take the RER C train to Palace of Versailles. Explore the Hall of Mirrors and the royal apartments.",
            "afternoon": "Wander the immaculate gardens and the Grand and Petit Trianon palaces.",
            "evening": "Return to Paris and enjoy a farewell dinner in the Latin Quarter.",
            "meals": {"breakfast": "Early breakfast before departure", "lunch": "Picnic in the Versailles gardens (~$15)", "dinner": "Bistro in the Latin Quarter (~$35)"},
            "highlights": ["Palace of Versailles", "Hall of Mirrors", "Versailles Gardens", "Grand Trianon"],
            "daily_cost": 280
        },
        {
            "day": 5, "title": "Day 5: Musée d'Orsay & Departure",
            "morning": "Visit the Musée d'Orsay for impressionist masterpieces — Monet, Renoir, Van Gogh.",
            "afternoon": "Last-minute shopping at Boulevard Haussmann department stores. Pick up macarons from Ladurée.",
            "evening": "Transfer to CDG for your departure flight.",
            "meals": {"breakfast": "Hotel breakfast", "lunch": "Café de Flore (~$30)", "dinner": "Airport dining"},
            "highlights": ["Musée d'Orsay", "Boulevard Haussmann", "Ladurée", "Palais Royal"],
            "daily_cost": 390
        }
    ]
})

with app.app_context():
    db.drop_all()
    db.create_all()

    # Sample user
    user = User(name="Alex Wanderer", email="demo@wanderai.com")
    user.set_password("password123")
    db.session.add(user)
    db.session.flush()

    # Sample trip
    trip = Trip(
        user_id=user.id,
        source="New York",
        destination="Paris",
        days=5,
        budget=1500,
        travelers=2,
        interests="Historical Places, Food, Nature",
        travel_dates="Dec 15 – Dec 20, 2025",
        itinerary=SAMPLE_ITINERARY,
        weather_data=json.dumps({
            "current": {"temp": 8, "feels_like": 5, "humidity": 72, "description": "Partly Cloudy", "icon": "02d", "wind_speed": 4.2},
            "forecast": [
                {"dt": 0, "temp_max": 10, "temp_min": 5, "description": "Cloudy", "icon": "03d"},
                {"dt": 0, "temp_max": 9, "temp_min": 4, "description": "Light Rain", "icon": "10d"},
                {"dt": 0, "temp_max": 11, "temp_min": 6, "description": "Sunny", "icon": "01d"},
                {"dt": 0, "temp_max": 12, "temp_min": 7, "description": "Partly Cloudy", "icon": "02d"},
                {"dt": 0, "temp_max": 10, "temp_min": 5, "description": "Overcast", "icon": "04d"}
            ]
        })
    )
    db.session.add(trip)
    db.session.commit()

    print("✅ Database initialized with sample user and trip.")
    print("   Login: demo@wanderai.com / password123")
