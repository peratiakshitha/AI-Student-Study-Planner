# AI Student Study Planner — No API Version

This Flask project creates a study timetable using the student's subjects, exam date, available daily hours, difficult subjects/topics and preferred study style.

**Important:** This version does not use Gemini, OpenAI, an API key, or paid billing. It uses rule-based scheduling. In your report and demo, describe it accurately as a rule-based study planner, not as an LLM-powered agent.

## Run on Windows / VS Code

1. Extract this ZIP file.
2. Open the `AI_Student_Study_Planner_No_API` folder in VS Code.
3. Select Terminal > New Terminal.
4. Run:

```powershell
python -m pip install -r requirements.txt
python app.py
```

5. Open http://127.0.0.1:5000 in your browser.
6. Keep the terminal open while using the website. Press Ctrl+C to stop it.

## Example input

- Subjects: DAA, DBMS, Computer Networks, Operating Systems
- Exam date: choose a future date
- Hours per day: 4
- Difficult subjects: DAA, DBMS
- Style: More time for difficult subjects

## Features

- Collects study details through a web form
- Checks exam date and daily study hours
- Allocates time across subjects
- Gives difficult subjects extra time when selected
- Rotates subject order each day
- Reserves the final day for revision
