from dataclasses import dataclass, field

DAYS_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


@dataclass
class TimeSlot:
    day: str
    start: int
    end: int

    @property
    def duration(self) -> int:
        return self.end - self.start


@dataclass
class Participant:
    name: str
    role: str
    slots: list = field(default_factory=list)


def minutes_to_time_str(minutes: int) -> str:
    h = minutes // 60
    m = minutes % 60
    period = "AM" if h < 12 else "PM"
    display_h = h % 12
    if display_h == 0:
        display_h = 12
    if m == 0:
        return f"{display_h} {period}"
    return f"{display_h}:{m:02d} {period}"


def parse_time(time_str: str) -> int:
    parts = time_str.split(":")
    return int(parts[0]) * 60 + int(parts[1])


def intersect(a: TimeSlot, b: TimeSlot) -> TimeSlot | None:
    if a.day != b.day:
        return None
    start = max(a.start, b.start)
    end = min(a.end, b.end)
    if start < end:
        return TimeSlot(day=a.day, start=start, end=end)
    return None


def find_common_slots(candidate: Participant, interviewers: list[Participant],
                      min_duration: int = 60) -> dict:
    all_slots = []
    conflicts = []

    for c_slot in candidate.slots:
        interviewer_overlaps = {}

        for iv in interviewers:
            best_overlap = None
            for iv_slot in iv.slots:
                overlap = intersect(c_slot, iv_slot)
                if overlap and overlap.duration >= min_duration:
                    if best_overlap is None or overlap.duration > best_overlap.duration:
                        best_overlap = overlap
            if best_overlap:
                interviewer_overlaps[iv.name] = best_overlap
            else:
                has_partial = False
                for iv_slot in iv.slots:
                    partial = intersect(c_slot, iv_slot)
                    if partial and partial.duration > 0:
                        has_partial = True
                        conflicts.append({
                            "description": (
                                f"{iv.name} overlaps with candidate on {c_slot.day} "
                                f"but only for {partial.duration} minutes "
                                f"({minutes_to_time_str(partial.start)}–{minutes_to_time_str(partial.end)}), "
                                f"which is less than the required {min_duration} minutes."
                            )
                        })
                if not has_partial:
                    conflicts.append({
                        "description": (
                            f"{iv.name} has no availability on {c_slot.day} "
                            f"during candidate's {minutes_to_time_str(c_slot.start)}–"
                            f"{minutes_to_time_str(c_slot.end)} window."
                        )
                    })

        if not interviewer_overlaps:
            continue

        events = []
        for name, ov in interviewer_overlaps.items():
            events.append((ov.start, 1, name))
            events.append((ov.end, -1, name))

        events.sort(key=lambda e: (e[0], e[1]))

        active = set()
        prev_time = None
        segments = []

        for time, delta, name in events:
            if prev_time is not None and prev_time < time and len(active) > 0:
                segments.append((prev_time, time, set(active)))
            if delta == 1:
                active.add(name)
            else:
                active.discard(name)
            prev_time = time

        merged = []
        for start, end, names in segments:
            if merged and merged[-1][2] == names and merged[-1][1] == start:
                merged[-1] = (merged[-1][0], end, names)
            else:
                merged.append((start, end, names))

        for start, end, available_names in merged:
            duration = end - start
            if duration < min_duration:
                continue
            missing = [iv.name for iv in interviewers if iv.name not in available_names]
            all_slots.append({
                "day": c_slot.day,
                "start": minutes_to_time_str(start),
                "end": minutes_to_time_str(end),
                "start_minutes": start,
                "end_minutes": end,
                "available_interviewers": sorted(available_names),
                "missing_interviewers": missing,
                "duration_minutes": duration,
                "interviewer_count": len(available_names),
            })

    all_slots.sort(key=lambda s: (
        -s["interviewer_count"],
        -s["duration_minutes"],
        DAYS_ORDER.index(s["day"]) if s["day"] in DAYS_ORDER else 99,
        s["start_minutes"],
    ))

    top_slots = all_slots[:3]

    for slot in top_slots:
        del slot["start_minutes"]
        del slot["end_minutes"]
        del slot["interviewer_count"]

    seen = set()
    unique_conflicts = []
    for c in conflicts:
        if c["description"] not in seen:
            seen.add(c["description"])
            unique_conflicts.append(c)

    recommendation = None
    if top_slots:
        best = top_slots[0]
        reasons = []
        if not best["missing_interviewers"]:
            reasons.append("all interviewers are available")
        else:
            reasons.append(
                f"{len(best['available_interviewers'])} of {len(interviewers)} interviewers are available"
            )
        reasons.append(f"it provides a {best['duration_minutes']}-minute window")
        if best["day"] in DAYS_ORDER:
            idx = DAYS_ORDER.index(best["day"])
            if idx < 3:
                reasons.append("it falls earlier in the week, allowing faster scheduling")

        recommendation = {
            "slot": best,
            "reasoning": (
                f"{best['day']} {best['start']}–{best['end']} is recommended because "
                + ", and ".join(reasons) + "."
            ),
        }

    return {
        "top_slots": top_slots,
        "conflicts": unique_conflicts,
        "recommendation": recommendation,
    }
