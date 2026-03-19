from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from scheduler import Participant, TimeSlot, parse_time, find_common_slots

app = Flask(__name__)
CORS(app)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/schedule", methods=["POST"])
def schedule():
    data = request.get_json()

    if not data:
        return jsonify({"error": "No JSON data provided"}), 400

    cand_data = data.get("candidate")
    if not cand_data or not cand_data.get("slots"):
        return jsonify({"error": "Candidate availability is required"}), 400

    candidate = Participant(
        name=cand_data.get("name", "Candidate"),
        role="candidate",
        slots=[
            TimeSlot(day=s["day"], start=parse_time(s["start"]), end=parse_time(s["end"]))
            for s in cand_data["slots"]
        ],
    )

    iv_data = data.get("interviewers", [])
    if len(iv_data) < 1:
        return jsonify({"error": "At least one interviewer is required"}), 400

    interviewers = []
    for iv in iv_data:
        if not iv.get("slots"):
            continue
        interviewers.append(Participant(
            name=iv.get("name", "Interviewer"),
            role="interviewer",
            slots=[
                TimeSlot(day=s["day"], start=parse_time(s["start"]), end=parse_time(s["end"]))
                for s in iv["slots"]
            ],
        ))

    if not interviewers:
        return jsonify({"error": "At least one interviewer with availability is required"}), 400

    min_duration = data.get("min_duration", 60)
    result = find_common_slots(candidate, interviewers, min_duration)
    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
