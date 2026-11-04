
from datetime import date, timedelta
from flask import Flask, request, render_template_string
from rag import retrieve_for_question

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
<title>AI Student Study Planner</title>
<meta name="viewport" content="width=device-width, initial-scale=1">

<style>
body {
    font-family: Arial, sans-serif;
    background: #f1f5fb;
    color: #1f2937;
    margin: 0;
}

header {
    background: #234a84;
    color: white;
    text-align: center;
    padding: 24px;
}

main {
    max-width: 900px;
    margin: 25px auto;
    padding: 0 14px;
}

.card {
    background: white;
    padding: 22px;
    border-radius: 12px;
    margin-bottom: 18px;
    box-shadow: 0 2px 12px #0001;
}

label {
    display: block;
    font-weight: bold;
    margin: 13px 0 6px;
}

input, textarea, select {
    width: 100%;
    padding: 11px;
    border: 1px solid #cbd5e1;
    border-radius: 7px;
    font-size: 15px;
    box-sizing: border-box;
}

textarea {
    min-height: 70px;
}

button {
    margin-top: 18px;
    background: #234a84;
    color: white;
    border: 0;
    padding: 12px 20px;
    border-radius: 7px;
    font-size: 16px;
    cursor: pointer;
}

button:hover {
    background: #16345f;
}

.day {
    border: 1px solid #dbe3ef;
    border-radius: 8px;
    padding: 14px;
    margin: 12px 0;
}

.day h3 {
    color: #234a84;
    margin-top: 0;
}

.error {
    color: #b91c1c;
    font-weight: bold;
}

.answer {
    background: #eef4ff;
    border-left: 4px solid #234a84;
    padding: 14px;
    margin: 12px 0;
    border-radius: 7px;
}

.stat {
    display: inline-block;
    background: #eef4ff;
    padding: 12px;
    margin: 5px;
    border-radius: 7px;
}

small {
    color: #64748b;
}
</style>
</head>

<body>

<header>
    <h1>AI Student Study Planner</h1>
    <div>Create your study timetable and ask study questions</div>
</header>

<main>

<!-- STUDY PLAN SECTION -->

<section class="card">

<h2>Generate Your Study Plan</h2>

<form method="POST">

<input type="hidden" name="action" value="plan">

<label>Student name (optional)</label>
<input name="name" value="{{v.name}}" placeholder="Your name">

<label>Subjects (separate with commas)</label>
<textarea name="subjects" required
placeholder="DAA, DBMS, Computer Networks">{{v.subjects}}</textarea>

<label>Exam date</label>
<input type="date" name="exam_date"
min="{{today}}" value="{{v.exam_date}}" required>

<label>Available study hours per day</label>
<input type="number" name="hours" min="1" max="16"
step="0.5" value="{{v.hours}}" required>

<label>Difficult subjects or topics (optional)</label>
<textarea name="difficult"
placeholder="DAA, DBMS normalization">{{v.difficult}}</textarea>

<label>Study plan style</label>

<select name="style">
<option value="balanced"
{% if v.style == 'balanced' %}selected{% endif %}>
Balanced
</option>

<option value="focus"
{% if v.style == 'focus' %}selected{% endif %}>
More time for difficult subjects
</option>

<option value="revision"
{% if v.style == 'revision' %}selected{% endif %}>
Revision focused
</option>
</select>

<button type="submit">Generate My Study Plan</button>

</form>

{% if error %}
<p class="error">{{error}}</p>
{% endif %}

</section>


<!-- AI QUESTION ANSWERING SECTION -->

<section class="card">

<h2>Ask Your AI Study Assistant</h2>

<p>Ask questions from DAA, DBMS, Computer Networks and Operating Systems.</p>

<form method="POST">

<input type="hidden" name="action" value="ask">

<label>Enter your question</label>

<textarea name="question" required
placeholder="Example: Explain the time complexity of binary search.">{{question}}</textarea>

<button type="submit">Ask AI</button>

</form>

{% if answer_error %}
<p class="error">{{answer_error}}</p>
{% endif %}

{% if answer_results %}

<h3>AI Retrieved Study Material</h3>

{% for result in answer_results %}

<div class="answer">

<p>{{result.text}}</p>

<small>
Source: {{result.source}}
</small>

<br>

<small>
Similarity score: {{result.score}}
</small>

</div>

{% endfor %}

{% endif %}

</section>


<!-- GENERATED TIMETABLE -->

{% if plan %}

<section class="card">

<h2>{{student}}'s Study Plan</h2>

<div class="stat">
<b>{{days}}</b> days available
</div>

<div class="stat">
<b>{{hours}}</b> hours per day
</div>

<p>
<small>
Generated using your subjects, exam date, study hours and selected plan style.
</small>
</p>

{% for day in plan %}

<div class="day">

<h3>Day {{loop.index}} — {{day.date}}</h3>

<ul>

{% for task in day.tasks %}

<li>
<b>{{task.subject}}</b> —
{{task.hours}} hour(s): {{task.detail}}
</li>

{% endfor %}

</ul>

</div>

{% endfor %}

<a href="/">Create another plan</a>

</section>

{% endif %}

</main>

</body>
</html>
"""


def split_subjects(text):
    return [
        x.strip()
        for x in text.replace("\\n", ",").split(",")
        if x.strip()
    ]


def build_plan(subjects, difficult, exam_date, hours, style):

    today = date.today()
    count = (exam_date - today).days + 1

    hard = [
        x.strip().lower()
        for x in difficult.replace("\\n", ",").split(",")
        if x.strip()
    ]

    weights = []

    for subject in subjects:
        is_hard = any(
            x in subject.lower() or subject.lower() in x
            for x in hard
        )

        weights.append(
            2 if is_hard and style == "focus"
            else 1.5 if is_hard and style == "balanced"
            else 1
        )

    total = sum(weights)
    result = []

    for d in range(count):

        current = today + timedelta(days=d)
        tasks = []

        if d == count - 1:

            tasks.append({
                "subject": "All subjects",
                "hours": hours,
                "detail": "Final revision, review important questions and formulas."
            })

        else:

            order = list(range(len(subjects)))
            shift = d % len(subjects)
            order = order[shift:] + order[:shift]

            allocations = [
                round(hours * weights[i] / total, 1)
                for i in range(len(subjects))
            ]

            diff = round(hours - sum(allocations), 1)
            allocations[order[0]] = round(
                allocations[order[0]] + diff, 1
            )

            for i in order:

                if style == "revision":
                    detail = "Revise notes and solve practice questions"

                elif weights[i] > 1:
                    detail = "Focus on difficult concepts and extra practice"

                else:
                    detail = "Learn key concepts and prepare short notes"

                tasks.append({
                    "subject": subjects[i],
                    "hours": allocations[i],
                    "detail": detail
                })

        result.append({
            "date": current.strftime("%d %b %Y"),
            "tasks": tasks
        })

    return result


@app.route("/", methods=["GET", "POST"])
def home():

    today = date.today()

    v = {
        "name": "",
        "subjects": "",
        "exam_date": "",
        "hours": "4",
        "difficult": "",
        "style": "balanced"
    }

    error = ""
    plan = []
    days = 0
    hours = ""
    student = "Your"

    question = ""
    answer_results = []
    answer_error = ""

    if request.method == "POST":

        action = request.form.get("action", "plan")

        # AI QUESTION ANSWERING

        if action == "ask":

            question = request.form.get("question", "").strip()

            if question:

                try:
                    answer_results = retrieve_for_question(
                        question,
                        top_k=3
                    )

                except Exception as e:
                    answer_error = (
                        "Unable to retrieve study material. "
                        "Check your RAG setup and try again."
                    )

                    print("RAG Error:", e)

            else:
                answer_error = "Please enter a question."

        # STUDY PLAN GENERATION

        else:

            for key in v:
                v[key] = request.form.get(
                    key, v[key]
                ).strip()

            student = v["name"] or "Your"

            try:

                subjects = split_subjects(v["subjects"])
                exam_date = date.fromisoformat(v["exam_date"])
                hours_value = float(v["hours"])

                if not subjects:
                    raise ValueError(
                        "Please enter at least one subject."
                    )

                if len(subjects) > 12:
                    raise ValueError(
                        "Please enter no more than 12 subjects."
                    )

                if exam_date < today:
                    raise ValueError(
                        "Exam date cannot be in the past."
                    )

                if not 1 <= hours_value <= 16:
                    raise ValueError(
                        "Enter between 1 and 16 study hours per day."
                    )

                plan = build_plan(
                    subjects,
                    v["difficult"],
                    exam_date,
                    hours_value,
                    v["style"]
                )

                days = (exam_date - today).days + 1
                hours = v["hours"]

            except (ValueError, TypeError):

                error = (
                    "Please enter valid details. "
                    "Check the subjects, exam date and study hours."
                )

    return render_template_string(
        HTML,
        v=v,
        today=today.isoformat(),
        error=error,
        plan=plan,
        days=days,
        hours=hours,
        student=student,
        question=question,
        answer_results=answer_results,
        answer_error=answer_error
    )

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
