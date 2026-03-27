import streamlit as st
from datetime import datetime, timedelta

#UI SETUP
st.set_page_config(page_title="Smart Study Planner", layout="centered")

st.title(" Smart Study Planner")
st.write("Plan your studies in a smart and realistic way with priorities given to topic and revision!")

#INPUT
num_subjects = st.number_input("Enter number of subjects", min_value=1, step=1)

subjects = {}
exam_dates = {}

for i in range(num_subjects):
    subject = st.text_input(f"Subject {i+1} name", key=f"sub{i}")

    if subject:
        num_topics = st.number_input(
            f"Number of topics in {subject}", min_value=1, step=1, key=f"top{i}"
        )

        topics = []

        for j in range(num_topics):
            topic_name = st.text_input(f"{subject} - Topic {j+1}", key=f"{subject}{j}")

            priority_label = st.selectbox(
                f"Priority for {topic_name if topic_name else f'Topic {j+1}'}",
                ["Low", "Medium", "High"],
                key=f"p{subject}{j}"
            )

            # Convert priority into number
            if priority_label == "Low":
                priority = 1
            elif priority_label == "Medium":
                priority = 2
            else:
                priority = 3

            if topic_name:
                topics.append({
                    "topic": topic_name,
                    "priority": priority
                })

        subjects[subject] = topics
        exam_dates[subject] = st.date_input(f"Exam date for {subject}", key=f"date{i}")

daily_hours = st.slider("Study hours per day", 1, 10, 4)

#GENERATE PLAN
if st.button("Generate Study Plan"):

    today = datetime.today()
    schedule = {}
    revision_days = 2

    all_tasks = []
    revision_schedule = {}

    #PREPARE TASKS
    for subject, topics in subjects.items():
        exam_date = datetime.combine(exam_dates[subject], datetime.min.time())

        # Add revision days before exam
        for i in range(revision_days):
            rev_day = (exam_date - timedelta(days=i + 1)).strftime("%Y-%m-%d")
            revision_schedule.setdefault(rev_day, []).append(f"🔁 {subject} - Revision")

        # Convert topics into tasks
        for t in topics:
            hours_needed = t["priority"] * 2  # High priority → more time

            all_tasks.append({
                "subject": subject,
                "topic": t["topic"],
                "priority": t["priority"],
                "hours": hours_needed,
                "exam_date": exam_date
            })

    # Sort tasks -> high priority first
    all_tasks.sort(key=lambda x: x["priority"], reverse=True)

    #SCHEDULING
    current_day = today

    for task in all_tasks:
        hours_left = task["hours"]

        while hours_left > 0:
            day_str = current_day.strftime("%Y-%m-%d")

            # 🚨 Stop scheduling after exam
            if current_day > task["exam_date"]:
                break

            # Skip revision days (already reserved)
            if day_str in revision_schedule:
                current_day += timedelta(days=1)
                continue

            # Create day entry if not exists
            schedule.setdefault(day_str, {"time_used": 0, "tasks": []})

            available_time = daily_hours - schedule[day_str]["time_used"]

            if available_time > 0:
                study_time = min(available_time, hours_left)

                # Human-friendly labels
                priority_text = {
                    1: "Low",
                    2: "Medium",
                    3: "High"
                }

                schedule[day_str]["tasks"].append(
                    f"{task['subject']} - {task['topic']} "
                    f"({study_time} hrs) [{priority_text[task['priority']]}]"
                )

                schedule[day_str]["time_used"] += study_time
                hours_left -= study_time
            else:
                current_day += timedelta(days=1)

    #ADD REVISION DAYS
    for day, tasks in revision_schedule.items():
        schedule.setdefault(day, {"time_used": 0, "tasks": []})
        schedule[day]["tasks"].extend(tasks)

    #OUTPUT
    st.subheader("Your Smart Study Plan")

    for day in sorted(schedule.keys()):
        st.markdown(f"###{day}")

        for task in schedule[day]["tasks"]:
            st.write(f"{task}")
