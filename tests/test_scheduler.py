from scheduler import Participant, TimeSlot, find_common_slots, minutes_to_time_str


def make_slot(day, start_h, start_m, end_h, end_m):
    return TimeSlot(day=day, start=start_h * 60 + start_m, end=end_h * 60 + end_m)


def test_basic_overlap():
    candidate = Participant("Candidate", "candidate", [make_slot("Tuesday", 14, 0, 17, 0)])
    interviewers = [
        Participant("Interviewer A", "interviewer", [make_slot("Tuesday", 15, 0, 18, 0)]),
        Participant("Interviewer B", "interviewer", [make_slot("Tuesday", 13, 0, 16, 0)]),
    ]
    result = find_common_slots(candidate, interviewers, min_duration=60)

    assert len(result["top_slots"]) >= 1
    best = result["top_slots"][0]
    assert best["day"] == "Tuesday"
    assert best["start"] == "3 PM"
    assert best["end"] == "4 PM"
    assert best["duration_minutes"] == 60
    assert set(best["available_interviewers"]) == {"Interviewer A", "Interviewer B"}
    assert best["missing_interviewers"] == []


def test_no_overlap():
    candidate = Participant("C", "candidate", [make_slot("Monday", 9, 0, 11, 0)])
    interviewers = [
        Participant("A", "interviewer", [make_slot("Tuesday", 14, 0, 16, 0)]),
    ]
    result = find_common_slots(candidate, interviewers)

    assert result["top_slots"] == []
    assert result["recommendation"] is None
    assert len(result["conflicts"]) > 0


def test_partial_overlap_under_min_duration():
    candidate = Participant("C", "candidate", [make_slot("Monday", 14, 0, 15, 0)])
    interviewers = [
        Participant("A", "interviewer", [make_slot("Monday", 14, 30, 16, 0)]),
    ]
    result = find_common_slots(candidate, interviewers, min_duration=60)

    assert result["top_slots"] == []
    assert len(result["conflicts"]) > 0


def test_multiple_days_ranking():
    candidate = Participant("C", "candidate", [
        make_slot("Tuesday", 14, 0, 17, 0),
        make_slot("Thursday", 14, 0, 17, 0),
    ])
    interviewers = [
        Participant("A", "interviewer", [make_slot("Thursday", 14, 0, 17, 0)]),
        Participant("B", "interviewer", [make_slot("Thursday", 14, 0, 17, 0)]),
        Participant("C_iv", "interviewer", [make_slot("Tuesday", 14, 0, 17, 0)]),
    ]
    result = find_common_slots(candidate, interviewers, min_duration=60)

    assert len(result["top_slots"]) >= 1
    best = result["top_slots"][0]
    assert best["day"] == "Thursday"


def test_identical_availability():
    slot = make_slot("Wednesday", 10, 0, 12, 0)
    candidate = Participant("C", "candidate", [slot])
    interviewers = [
        Participant("A", "interviewer", [make_slot("Wednesday", 10, 0, 12, 0)]),
        Participant("B", "interviewer", [make_slot("Wednesday", 10, 0, 12, 0)]),
    ]
    result = find_common_slots(candidate, interviewers, min_duration=60)

    assert len(result["top_slots"]) >= 1
    best = result["top_slots"][0]
    assert best["duration_minutes"] == 120
    assert len(best["missing_interviewers"]) == 0


def test_three_interviewers_partial():
    candidate = Participant("C", "candidate", [make_slot("Friday", 9, 0, 12, 0)])
    interviewers = [
        Participant("A", "interviewer", [make_slot("Friday", 9, 0, 11, 0)]),
        Participant("B", "interviewer", [make_slot("Friday", 10, 0, 12, 0)]),
        Participant("D", "interviewer", [make_slot("Monday", 9, 0, 12, 0)]),
    ]
    result = find_common_slots(candidate, interviewers, min_duration=60)

    assert len(result["top_slots"]) >= 1
    for slot in result["top_slots"]:
        if slot["day"] == "Friday":
            assert "D" in slot["missing_interviewers"]


def test_minutes_to_time_str():
    assert minutes_to_time_str(0) == "12 AM"
    assert minutes_to_time_str(540) == "9 AM"
    assert minutes_to_time_str(720) == "12 PM"
    assert minutes_to_time_str(810) == "1:30 PM"
    assert minutes_to_time_str(1020) == "5 PM"


def test_recommendation_present():
    candidate = Participant("C", "candidate", [make_slot("Tuesday", 14, 0, 17, 0)])
    interviewers = [
        Participant("A", "interviewer", [make_slot("Tuesday", 15, 0, 18, 0)]),
    ]
    result = find_common_slots(candidate, interviewers, min_duration=60)

    assert result["recommendation"] is not None
    assert "reasoning" in result["recommendation"]
    assert result["recommendation"]["slot"]["day"] == "Tuesday"
