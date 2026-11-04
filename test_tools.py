
from tools import study_tools

# Tool 1: Analyze subjects
print("\n--- SUBJECT ANALYSIS ---")
print(study_tools[0].invoke({
    "subjects": ["DAA", "DBMS", "CN", "OS"],
    "difficult_subjects": ["DAA", "DBMS"]
}))

# Tool 2: Generate schedule
print("\n--- STUDY SCHEDULE ---")
print(study_tools[1].invoke({
    "subjects": ["DAA", "DBMS", "CN", "OS"],
    "study_hours": 4,
    "difficult_subjects": ["DAA", "DBMS"]
}))

# Tool 3: Track progress
print("\n--- STUDY PROGRESS ---")
print(study_tools[2].invoke({
    "completed": 3,
    "total": 5
}))
