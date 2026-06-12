import os
import json
import re
import requests
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models.models import db, User, Trip

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-me')
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database', 'travel_planner.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY', '')


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ─── Auth Routes ────────────────────────────────────────────────────────────

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')
        if not all([name, email, password, confirm]):
            flash('All fields are required.', 'danger')
        elif password != confirm:
            flash('Passwords do not match.', 'danger')
        elif len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
        elif User.query.filter_by(email=email).first():
            flash('Email already registered. Please log in.', 'warning')
        else:
            user = User(name=name, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash('Account created! Welcome aboard.', 'success')
            login_user(user)
            return redirect(url_for('dashboard'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user, remember=request.form.get('remember'))
            next_page = request.args.get('next')
            flash(f'Welcome back, {user.name}!', 'success')
            return redirect(next_page or url_for('dashboard'))
        flash('Invalid email or password.', 'danger')
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


# ─── Main Routes ────────────────────────────────────────────────────────────

@app.route('/dashboard')
@login_required
def dashboard():
    query = request.args.get('q', '').strip()
    filter_days = request.args.get('days', '')
    trips_query = Trip.query.filter_by(user_id=current_user.id)
    if query:
        trips_query = trips_query.filter(Trip.destination.ilike(f'%{query}%'))
    if filter_days:
        try:
            trips_query = trips_query.filter(Trip.days == int(filter_days))
        except ValueError:
            pass
    trips = trips_query.order_by(Trip.created_at.desc()).all()
    return render_template('dashboard.html', trips=trips, query=query, filter_days=filter_days)


@app.route('/plan', methods=['GET', 'POST'])
@login_required
def plan_trip():
    if request.method == 'POST':
        source = request.form.get('source', '').strip()
        destination = request.form.get('destination', '').strip()
        days = request.form.get('days', '3')
        budget = request.form.get('budget', '1000')
        travelers = request.form.get('travelers', '1')
        interests = request.form.getlist('interests')
        travel_dates = request.form.get('travel_dates', '').strip()

        if not destination:
            flash('Please enter a destination.', 'danger')
            return render_template('plan_trip.html')

        try:
            days_int = int(days)
            budget_float = float(budget)
            travelers_int = int(travelers)
        except ValueError:
            flash('Invalid numeric values provided.', 'danger')
            return render_template('plan_trip.html')

        interests_str = ', '.join(interests) if interests else 'General sightseeing'

        itinerary = generate_itinerary(
            source, destination, days_int, budget_float,
            travelers_int, interests_str, travel_dates
        )
        weather = get_weather(destination)

        trip = Trip(
            user_id=current_user.id,
            source=source,
            destination=destination,
            days=days_int,
            budget=budget_float,
            travelers=travelers_int,
            interests=interests_str,
            travel_dates=travel_dates,
            itinerary=itinerary,
            weather_data=json.dumps(weather)
        )
        db.session.add(trip)
        db.session.commit()

        return redirect(url_for('view_trip', trip_id=trip.trip_id))

    return render_template('plan_trip.html')


@app.route('/trip/<int:trip_id>')
@login_required
def view_trip(trip_id):
    trip = Trip.query.filter_by(trip_id=trip_id, user_id=current_user.id).first_or_404()
    weather = None
    if trip.weather_data:
        try:
            weather = json.loads(trip.weather_data)
        except Exception:
            weather = None
    return render_template('view_trip.html', trip=trip, weather=weather)


@app.route('/trip/<int:trip_id>/delete', methods=['POST'])
@login_required
def delete_trip(trip_id):
    trip = Trip.query.filter_by(trip_id=trip_id, user_id=current_user.id).first_or_404()
    db.session.delete(trip)
    db.session.commit()
    flash('Trip deleted.', 'success')
    return redirect(url_for('dashboard'))


# ─── API Helpers ────────────────────────────────────────────────────────────

def generate_itinerary(source, destination, days, budget, travelers, interests, travel_dates):
    prompt = f"""You are an expert travel planner. Create a detailed {days}-day travel itinerary.

Trip Details:
- From: {source if source else 'Not specified'}
- To: {destination}
- Duration: {days} days
- Total Budget: ${budget} USD for {travelers} traveler(s) (${budget/travelers:.0f} per person)
- Interests: {interests}
- Travel Dates: {travel_dates if travel_dates else 'Flexible'}

Provide a comprehensive itinerary in this EXACT JSON format (return only valid JSON, no markdown):
{{
  "overview": "Brief 2-sentence destination overview",
  "budget_breakdown": {{
    "accommodation": <number>,
    "food": <number>,
    "transportation": <number>,
    "activities": <number>,
    "miscellaneous": <number>,
    "total": <number>
  }},
  "travel_tips": ["tip1", "tip2", "tip3", "tip4", "tip5"],
  "days": [
    {{
      "day": 1,
      "title": "Day title",
      "morning": "Morning activities description",
      "afternoon": "Afternoon activities description",
      "evening": "Evening activities description",
      "meals": {{
        "breakfast": "Recommendation",
        "lunch": "Recommendation",
        "dinner": "Recommendation"
      }},
      "highlights": ["attraction1", "attraction2"],
      "daily_cost": <number>
    }}
  ]
}}

Make recommendations specific to {destination}, aligned with {interests} interests and the ${budget} budget."""

    if GEMINI_API_KEY and GEMINI_API_KEY != 'your-gemini-api-key-here':
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.7, "maxOutputTokens": 4096}
            }
            resp = requests.post(url, json=payload, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                text = data['candidates'][0]['content']['parts'][0]['text']
                text = re.sub(r'```json\s*|\s*```', '', text).strip()
                json.loads(text)  # validate
                return text
        except Exception as e:
            print(f"Gemini API error: {e}")

    # Fallback demo itinerary
    return generate_demo_itinerary(destination, days, budget, travelers, interests)


def generate_demo_itinerary(destination, days, budget, travelers, interests):
    per_person = budget / travelers
    daily = per_person / days
    itinerary = {
        "overview": f"Welcome to {destination}! This vibrant destination offers a perfect blend of culture, history, and adventure tailored to your interests in {interests}.",
        "budget_breakdown": {
            "accommodation": round(budget * 0.35, 2),
            "food": round(budget * 0.25, 2),
            "transportation": round(budget * 0.20, 2),
            "activities": round(budget * 0.15, 2),
            "miscellaneous": round(budget * 0.05, 2),
            "total": budget
        },
        "travel_tips": [
            f"Book accommodations in {destination} at least 2 weeks in advance for better rates.",
            "Carry local currency for small vendors and markets.",
            "Download offline maps before your trip to navigate without data.",
            "Try the local street food — it's often the most authentic experience.",
            "Respect local customs and dress codes, especially at religious sites."
        ],
        "days": []
    }
    day_themes = [
        ("Arrival & City Exploration", "Explore the city center and iconic landmarks"),
        ("Cultural Immersion", "Dive into local culture, museums, and heritage"),
        ("Nature & Adventure", "Outdoor activities and scenic spots"),
        ("Local Markets & Food Trail", "Culinary experiences and shopping"),
        ("Hidden Gems", "Off-the-beaten-path discoveries"),
        ("Day Trip", "Excursion to a nearby attraction"),
        ("Leisure & Departure Prep", "Relax, last-minute shopping, and memories")
    ]
    for i in range(days):
        theme_idx = i % len(day_themes)
        title, desc = day_themes[theme_idx]
        itinerary["days"].append({
            "day": i + 1,
            "title": f"Day {i+1}: {title}",
            "morning": f"Start the morning exploring {destination}'s highlights related to {desc.lower()}. Visit key landmarks and soak in the atmosphere.",
            "afternoon": f"After lunch, continue with afternoon activities — visit local attractions, interact with residents, and enjoy the scenery.",
            "evening": f"Wind down with a pleasant evening experience — a sunset viewpoint, local market, or a relaxed dinner at a recommended restaurant.",
            "meals": {
                "breakfast": "Local café with traditional breakfast options",
                "lunch": f"Mid-range restaurant near the day's attractions (~${daily*0.2:.0f})",
                "dinner": f"Evening dining experience at a popular local eatery (~${daily*0.3:.0f})"
            },
            "highlights": [f"{destination} Landmark {i+1}", "Local Cultural Site", "Scenic Viewpoint"],
            "daily_cost": round(daily, 2)
        })
    return json.dumps(itinerary)


def get_weather(city):
    if OPENWEATHER_API_KEY and OPENWEATHER_API_KEY != 'your-openweather-api-key-here':
        try:
            url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={OPENWEATHER_API_KEY}&units=metric&cnt=5"
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                current_url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
                curr = requests.get(current_url, timeout=10).json()
                return {
                    "current": {
                        "temp": round(curr['main']['temp']),
                        "feels_like": round(curr['main']['feels_like']),
                        "humidity": curr['main']['humidity'],
                        "description": curr['weather'][0]['description'].title(),
                        "icon": curr['weather'][0]['icon'],
                        "wind_speed": curr['wind']['speed']
                    },
                    "forecast": [
                        {
                            "dt": item['dt'],
                            "temp_max": round(item['main']['temp_max']),
                            "temp_min": round(item['main']['temp_min']),
                            "description": item['weather'][0]['description'].title(),
                            "icon": item['weather'][0]['icon']
                        } for item in data['list'][::8][:5]
                    ]
                }
        except Exception as e:
            print(f"Weather API error: {e}")
    # Demo weather
    return {
        "current": {
            "temp": 26, "feels_like": 28, "humidity": 65,
            "description": "Partly Cloudy", "icon": "02d", "wind_speed": 3.5
        },
        "forecast": [
            {"dt": 0, "temp_max": 29, "temp_min": 22, "description": "Sunny", "icon": "01d"},
            {"dt": 0, "temp_max": 27, "temp_min": 21, "description": "Cloudy", "icon": "03d"},
            {"dt": 0, "temp_max": 25, "temp_min": 20, "description": "Light Rain", "icon": "10d"},
            {"dt": 0, "temp_max": 28, "temp_min": 22, "description": "Partly Cloudy", "icon": "02d"},
            {"dt": 0, "temp_max": 30, "temp_min": 23, "description": "Sunny", "icon": "01d"}
        ]
    }


if __name__ == '__main__':
    with app.app_context():
        os.makedirs('database', exist_ok=True)
        db.create_all()
        print("✅ Database initialized.")
    app.run(debug=True, port=5000)
