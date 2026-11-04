
from typing import TypedDict

from langgraph.graph import StateGraph, START, END

from tools import (
    analyze_subjects,
    generate_study_schedule,
    track_study_progress
)

from rag import retrieve_for_question


# 1. Define shared state
class StudyState(TypedDict):
    subjects: list[str]
    difficult_subjects: list[str]
    study_hours: float
    completed_tasks: int
    total_tasks: int
    question: str

    subject_analysis: str
    study_schedule: str
    progress_report: str
    retrieved_materials: str


# 2. Analyze subjects
def analyze_node(state: StudyState):

    result = analyze_subjects.invoke({
        "subjects": state["subjects"],
        "difficult_subjects": state["difficult_subjects"]
    })

    return {"subject_analysis": result}


# 3. Generate schedule
def schedule_node(state: StudyState):

    result = generate_study_schedule.invoke({
        "subjects": state["subjects"],
        "study_hours": state["study_hours"],
        "difficult_subjects": state["difficult_subjects"]
    })

    return {"study_schedule": result}


# 4. Track progress
def progress_node(state: StudyState):

    result = track_study_progress.invoke({
        "completed": state["completed_tasks"],
        "total": state["total_tasks"]
    })

    return {"progress_report": result}


# 5. Retrieve study materials using RAG
def rag_node(state: StudyState):

    results = retrieve_for_question(
        state["question"],
        top_k=3
    )

    output = []

    for item in results:
        output.append(
            f"Source: {item['source']}\n"
            f"Similarity: {item['score']:.3f}\n"
            f"Content: {item['text']}"
        )

    return {
        "retrieved_materials": "\n\n".join(output)
    }


# 6. Build LangGraph
builder = StateGraph(StudyState)

builder.add_node("analyze", analyze_node)
builder.add_node("schedule", schedule_node)
builder.add_node("progress", progress_node)
builder.add_node("rag", rag_node)

builder.add_edge(START, "analyze")
builder.add_edge("analyze", "schedule")
builder.add_edge("schedule", "progress")
builder.add_edge("progress", "rag")
builder.add_edge("rag", END)

study_graph = builder.compile()


# 7. Execute workflow
if __name__ == "__main__":

    student_input = {
        "subjects": ["DAA", "DBMS", "CN", "OS"],
        "difficult_subjects": ["DAA", "DBMS"],
        "study_hours": 4,
        "completed_tasks": 3,
        "total_tasks": 5,
        "question": "What is the time complexity of binary search?",

        "subject_analysis": "",
        "study_schedule": "",
        "progress_report": "",
        "retrieved_materials": ""
    }

    result = study_graph.invoke(student_input)

    print("\n===== AI STUDENT STUDY PLANNER =====")

    print("\n1. SUBJECT ANALYSIS")
    print(result["subject_analysis"])

    print("\n2. PERSONALIZED STUDY SCHEDULE")
    print(result["study_schedule"])

    print("\n3. STUDY PROGRESS")
    print(result["progress_report"])

    print("\n4. RAG STUDY MATERIAL RETRIEVAL")
    print(result["retrieved_materials"])

    print("\n===== WORKFLOW COMPLETED =====")
