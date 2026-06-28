# WanderAI — AI Travel Planner

A full-stack AI-powered travel planner built with Python Flask, SQLite, Bootstrap 5, and Gemini AI.

---

## 🚀 Quick Start

### 1. Create & activate a virtual environment

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure API keys

Edit the `.env` file:

```env
SECRET_KEY=your-secure-random-key
GEMINI_API_KEY=your-gemini-api-key-here
OPENWEATHER_API_KEY=your-openweather-api-key-here
```

**Get API keys:**
- **Gemini AI:** https://aistudio.google.com/app/apikey (free tier available)
- **OpenWeather:** https://openweathermap.org/api (free tier available)

> The app works without API keys — it uses built-in demo data as fallback.

### 4. Initialize the database (with sample data)

```bash
python init_db.py
```

This creates:
- `database/travel_planner.db`
- Sample user: `demo@wanderai.com` / `password123`
- One sample India trip (demo itinerary seeded)

### 5. Run the app

```bash
python app.py
```

Visit: http://localhost:5000

---

## 🚢 Deployment

### Docker

Build and run the container:

```bash
docker build -t travel_planner_app .
docker run -p 5000:5000 --env-file .env travel_planner_app
```

Open http://localhost:5000.

### Heroku

1. Install the Heroku CLI: https://devcenter.heroku.com/articles/heroku-cli
2. Log in: `heroku login`
3. Create an app:

```bash
heroku create your-app-name
```

4. Push your code:

```bash
git init
heroku git:remote -a your-app-name
git add .
git commit -m "Deploy travel planner"
git push heroku main
```

5. Set config vars:

```bash
heroku config:set SECRET_KEY=your-secret-key
heroku config:set GEMINI_API_KEY=your-gemini-api-key
heroku config:set OPENWEATHER_API_KEY=your-openweather-api-key
```

6. Open the app:

```bash
heroku open
```

> If you use Heroku, the `Procfile` ensures Gunicorn starts the app.

---

## 📁 Project Structure

```
travel_planner/
├── app.py                  # Flask app, routes, AI + weather API calls
├── init_db.py              # Database initializer with sample data
├── requirements.txt
├── .env                    # API keys (never commit this)
├── models/
│   ├── __init__.py
│   └── models.py           # SQLAlchemy User + Trip models
├── templates/
│   ├── base.html           # Shared layout with navbar
│   ├── index.html          # Landing page
│   ├── login.html
│   ├── register.html
│   ├── plan_trip.html      # Trip planning form
│   ├── view_trip.html      # Itinerary viewer
│   └── dashboard.html      # My Trips dashboard
├── static/
│   ├── css/style.css       # Full custom stylesheet
│   └── js/
│       ├── main.js         # Global JS helpers
│       └── trip.js         # JSON itinerary renderer
└── database/
    ├── schema.sql          # SQL schema reference
    └── travel_planner.db   # Auto-created SQLite database
```

---

## 🗄️ Database Tables

### users
| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | Auto-increment |
| name | TEXT | Full name |
| email | TEXT UNIQUE | Login email |
| password | TEXT | bcrypt hash |
| created_at | DATETIME | Auto |

### trips
| Column | Type | Notes |
|--------|------|-------|
| trip_id | INTEGER PK | Auto-increment |
| user_id | INTEGER FK | → users.id |
| source | TEXT | Departure city |
| destination | TEXT | Target city |
| days | INTEGER | Trip duration |
| budget | REAL | Total USD budget |
| travelers | INTEGER | Number of people |
| interests | TEXT | Comma-separated |
| travel_dates | TEXT | Free-text dates |
| itinerary | TEXT | JSON itinerary |
| weather_data | TEXT | JSON weather |
| created_at | DATETIME | Auto |

---

## ✨ Features

- **User auth** — Register, login, sessions, password hashing
- **AI itinerary** — Gemini 1.5 Flash generates day-by-day plans for Indian destinations only
- **Budget breakdown** — Visual bars for accommodation, food, transport, activities, all shown in INR
- **Weather** — OpenWeather current + 5-day forecast
- **Dashboard** — All trips, search by destination, filter by duration, delete
- **Responsive** — Mobile-friendly via Bootstrap 5
- **Fallback mode** — Works fully offline with demo data when no API keys are set

---

## 🔑 Environment Variables

| Variable | Purpose |
|----------|---------|
| `SECRET_KEY` | Flask session encryption |
| `GEMINI_API_KEY` | Gemini 1.5 Flash for itinerary generation |
| `OPENWEATHER_API_KEY` | Current weather + forecast |
