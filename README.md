# Interview Scheduling Automation

A Flask web app that finds common interview time slots between a candidate and one or more interviewers. It returns the top 3 ranked slots along with conflict explanations and a recommendation.

## Features

- Accepts availability windows for a candidate and multiple interviewers
- Uses a sweep-line algorithm to find overlapping intervals
- Ranks slots by interviewer count, duration, and day/time
- Returns a human-readable recommendation with reasoning
- Highlights partial overlaps and conflicts

## Project Structure

```
.
├── app.py           # Flask app & API routes
├── scheduler.py     # Core scheduling algorithm
├── requirements.txt
├── static/          # Frontend assets
├── templates/       # Jinja2 HTML templates
└── tests/           # Pytest test suite
```

## Getting Started

### 1. Create and activate a virtual environment

```bash
python -m venv venv
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the app

```bash
python app.py
```

The app will be available at `http://localhost:5000`.

## API

### `POST /api/schedule`

**Request body:**

```json
{
  "candidate": {
    "name": "Alice",
    "slots": [
      { "day": "Monday", "start": "09:00", "end": "12:00" }
    ]
  },
  "interviewers": [
    {
      "name": "Bob",
      "slots": [
        { "day": "Monday", "start": "10:00", "end": "13:00" }
      ]
    }
  ],
  "min_duration": 60
}
```

- `day` — Full weekday name (e.g. `"Monday"`)
- `start` / `end` — 24-hour `HH:MM` format
- `min_duration` — Minimum slot length in minutes (default: `60`)

**Response:**

```json
{
  "top_slots": [...],
  "conflicts": [...],
  "recommendation": {
    "slot": { ... },
    "reasoning": "Monday 10 AM–12 PM is recommended because ..."
  }
}
```

## Running Tests

```bash
pytest
```
