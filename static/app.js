
const DAYS = [
    { value: "Monday", label: "Mon" },
    { value: "Tuesday", label: "Tue" },
    { value: "Wednesday", label: "Wed" },
    { value: "Thursday", label: "Thu" },
    { value: "Friday", label: "Fri" },
    { value: "Saturday", label: "Sat" },
    { value: "Sunday", label: "Sun" },
];

let interviewerCount = 0;

function createSlotRow(day = "Tuesday", start = "14:00", end = "17:00") {
    const row = document.createElement("div");
    row.className = "slot-row";

    const daySelect = document.createElement("select");
    daySelect.className = "day-select";
    DAYS.forEach(d => {
        const opt = document.createElement("option");
        opt.value = d.value;
        opt.textContent = d.label;
        if (d.value === day) opt.selected = true;
        daySelect.appendChild(opt);
    });

    const startInput = document.createElement("input");
    startInput.type = "time";
    startInput.className = "time-start";
    startInput.value = start;

    const sep = document.createElement("span");
    sep.className = "time-sep";
    sep.textContent = "to";

    const endInput = document.createElement("input");
    endInput.type = "time";
    endInput.className = "time-end";
    endInput.value = end;

    const removeBtn = document.createElement("button");
    removeBtn.className = "btn-icon btn-remove-slot";
    removeBtn.title = "Remove";
    removeBtn.innerHTML = "&times;";
    removeBtn.addEventListener("click", () => {
        const container = row.parentElement;
        if (container.children.length > 1) {
            row.remove();
        }
    });

    row.append(daySelect, startInput, sep, endInput, removeBtn);
    return row;
}

function createInterviewerEntry(name, day = "Tuesday", start = "15:00", end = "18:00") {
    interviewerCount++;
    const entry = document.createElement("div");
    entry.className = "interviewer-entry";
    entry.dataset.id = interviewerCount;

    const header = document.createElement("div");
    header.className = "entry-header";

    const nameInput = document.createElement("input");
    nameInput.type = "text";
    nameInput.className = "name-input";
    nameInput.placeholder = "Interviewer name";
    nameInput.value = name;

    const removeBtn = document.createElement("button");
    removeBtn.className = "btn-remove-interviewer";
    removeBtn.textContent = "Remove";
    removeBtn.addEventListener("click", () => {
        const container = document.getElementById("interviewers-container");
        if (container.children.length > 1) {
            entry.remove();
        }
    });

    header.append(removeBtn);

    const slotsContainer = document.createElement("div");
    slotsContainer.className = "slots-container";
    slotsContainer.appendChild(createSlotRow(day, start, end));

    const addSlotBtn = document.createElement("button");
    addSlotBtn.className = "btn-secondary btn-add-slot";
    addSlotBtn.textContent = "+ Add time slot";
    addSlotBtn.addEventListener("click", () => {
        slotsContainer.appendChild(createSlotRow("Tuesday", "09:00", "12:00"));
    });

    entry.append(nameInput, header, slotsContainer, addSlotBtn);
    return entry;
}

function readSlots(container) {
    const rows = container.querySelectorAll(".slot-row");
    const slots = [];
    rows.forEach(row => {
        const day = row.querySelector(".day-select").value;
        const start = row.querySelector(".time-start").value;
        const end = row.querySelector(".time-end").value;
        if (day && start && end && start < end) {
            slots.push({ day, start, end });
        }
    });
    return slots;
}

function collectData() {
    const candidateName = document.getElementById("candidate-name").value || "Candidate";
    const candidateSlots = readSlots(document.getElementById("candidate-slots"));

    const interviewerEntries = document.querySelectorAll(".interviewer-entry");
    const interviewers = [];
    interviewerEntries.forEach(entry => {
        const name = entry.querySelector(".name-input").value || "Interviewer";
        const slots = readSlots(entry.querySelector(".slots-container"));
        if (slots.length > 0) {
            interviewers.push({ name, slots });
        }
    });

    return {
        candidate: { name: candidateName, slots: candidateSlots },
        interviewers,
        min_duration: parseInt(document.getElementById("min-duration").value),
    };
}

function renderResults(data) {
    const section = document.getElementById("results");
    section.classList.remove("hidden");
    section.scrollIntoView({ behavior: "smooth", block: "start" });

    const recBody = document.getElementById("recommendation-body");
    if (data.recommendation) {
        const r = data.recommendation;
        recBody.innerHTML = `
            <div class="rec-slot">${r.slot.day} ${r.slot.start} – ${r.slot.end}</div>
            <div class="rec-reasoning">${r.reasoning}</div>
            <div class="rec-interviewers">
                Available: ${r.slot.available_interviewers.map(n => `<span>${n}</span>`).join("")}
                ${r.slot.missing_interviewers.length > 0
                    ? `<br>Missing: ${r.slot.missing_interviewers.map(n => `<span style="background:#fef3c7;color:#92400e">${n}</span>`).join("")}`
                    : ""}
            </div>
        `;
    } else {
        recBody.innerHTML = `<div class="no-results"><h3>No matching slots found</h3><p>Try adjusting availability windows or reducing the minimum duration.</p></div>`;
    }

    const topSlotsEl = document.getElementById("top-slots");
    if (data.top_slots.length === 0) {
        topSlotsEl.innerHTML = `<div class="no-results"><p>No valid time slots found.</p></div>`;
    } else {
        topSlotsEl.innerHTML = data.top_slots.map((slot, i) => `
            <div class="slot-card">
                <div class="slot-rank rank-${i + 1}">#${i + 1}</div>
                <div class="slot-details">
                    <div class="slot-time">${slot.day} ${slot.start} – ${slot.end}</div>
                    <div class="slot-meta">
                        <span class="available">${slot.available_interviewers.length} interviewer${slot.available_interviewers.length !== 1 ? "s" : ""} available: ${slot.available_interviewers.join(", ")}</span>
                        ${slot.missing_interviewers.length > 0
                            ? `<br><span class="missing">Missing: ${slot.missing_interviewers.join(", ")}</span>`
                            : ""}
                        <br>${slot.duration_minutes} min window
                    </div>
                </div>
            </div>
        `).join("");
    }

    const conflictsSection = document.getElementById("conflicts-section");
    const conflictsBody = document.getElementById("conflicts-body");
    if (data.conflicts.length > 0) {
        conflictsSection.classList.remove("hidden");
        conflictsBody.innerHTML = data.conflicts.map(c =>
            `<div class="conflict-item"><span class="conflict-icon">!</span> ${c.description}</div>`
        ).join("");
    } else {
        conflictsSection.classList.add("hidden");
    }
}

document.addEventListener("DOMContentLoaded", () => {
    const container = document.getElementById("interviewers-container");

    container.appendChild(createInterviewerEntry("Interviewer A", "Tuesday", "15:00", "18:00"));
    container.appendChild(createInterviewerEntry("Interviewer B", "Tuesday", "13:00", "16:00"));
    container.appendChild(createInterviewerEntry("Interviewer C", "Wednesday", "10:00", "14:00"));

    document.querySelector('.btn-add-slot[data-target="candidate-slots"]').addEventListener("click", () => {
        document.getElementById("candidate-slots").appendChild(createSlotRow("Wednesday", "09:00", "12:00"));
    });

    document.getElementById("add-interviewer").addEventListener("click", () => {
        if (container.children.length >= 5) {
            alert("Maximum 5 interviewers allowed.");
            return;
        }
        container.appendChild(createInterviewerEntry(`Interviewer ${String.fromCharCode(65 + container.children.length)}`, "Tuesday", "09:00", "12:00"));
    });

    document.getElementById("find-slots").addEventListener("click", async () => {
        const data = collectData();

        if (data.candidate.slots.length === 0) {
            alert("Please add at least one time slot for the candidate.");
            return;
        }
        if (data.interviewers.length === 0) {
            alert("Please add at least one interviewer with time slots.");
            return;
        }

        const btn = document.getElementById("find-slots");
        btn.classList.add("loading");
        btn.textContent = "Finding...";

        try {
            const res = await fetch("/api/schedule", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(data),
            });
            const result = await res.json();

            if (result.error) {
                alert(result.error);
            } else {
                renderResults(result);
            }
        } catch (err) {
            alert("Failed to connect to server. Is it running?");
        } finally {
            btn.classList.remove("loading");
            btn.textContent = "Find Best Slots";
        }
    });
});
