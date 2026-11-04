
from langchain_core.tools import tool


@tool
def analyze_subjects(subjects: list[str], difficult_subjects: list[str]) -> str:
    """Analyze subjects and identify which subjects need more study attention."""

    difficult = {s.strip().lower() for s in difficult_subjects}

    result = []

    for subject in subjects:
        if subject.strip().lower() in difficult:
            result.append(f"{subject}: High Priority")
        else:
            result.append(f"{subject}: Normal Priority")

    return "\n".join(result)


@tool
def generate_study_schedule(
    subjects: list[str],
    study_hours: float,
    difficult_subjects: list[str]
) -> str:
    """Generate a daily study schedule based on subjects and available hours."""

    if not subjects:
        return "No subjects provided."

    if study_hours <= 0:
        return "Study hours must be greater than zero."

    difficult = {s.strip().lower() for s in difficult_subjects}

    weights = [
        2 if subject.strip().lower() in difficult else 1
        for subject in subjects
    ]

    total_weight = sum(weights)
    allocations = [
        study_hours * weight / total_weight
        for weight in weights
    ]

    result = ["Personalized Daily Study Schedule"]

    for subject, hours in zip(subjects, allocations):
        result.append(f"{subject}: {hours:.2f} hours")

    return "\n".join(result)


@tool
def track_study_progress(completed: int, total: int) -> str:
    """Calculate the percentage of completed study tasks."""

    if total <= 0:
        return "Total tasks must be greater than zero."

    if completed < 0 or completed > total:
        return "Completed tasks must be between zero and total tasks."

    percentage = (completed / total) * 100

    return (
        f"Completed tasks: {completed}/{total}\n"
        f"Study progress: {percentage:.1f}%"
    )


# Register all tools
study_tools = [
    analyze_subjects,
    generate_study_schedule,
    track_study_progress
]
