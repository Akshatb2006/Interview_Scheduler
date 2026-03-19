# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Interview Scheduling Automation — a Flask web app that finds optimal interview time slots given candidate and interviewer availability. No database; all data is ephemeral per request.

## Commands

```bash
# Setup
python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt

# Run server (serves UI at http://localhost:5000)
source venv/bin/activate && python3 app.py

# Run tests
source venv/bin/activate && pytest tests/ -v
```

## Architecture

- `scheduler.py` — Pure scheduling algorithm (no Flask dependency). Contains `find_common_slots()` which uses a sweep-line approach to find interval intersections, ranks by interviewer count then duration, and returns top 3 slots + conflicts + recommendation.
- `app.py` — Flask app with two routes: `GET /` (serves dashboard) and `POST /api/schedule` (JSON in, JSON out). Thin wrapper that parses input and calls into `scheduler.py`.
- `templates/index.html` + `static/style.css` + `static/app.js` — Single-page vanilla HTML/CSS/JS frontend. No build step. Two input panels (candidate + interviewers) and a results section with recommendation, ranked slots, and conflicts.
- Time is handled as minutes-from-midnight internally; 24h format (`HH:MM`) over the API; 12h format for display.
