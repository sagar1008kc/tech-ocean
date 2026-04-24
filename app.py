import json
from pathlib import Path
from io import StringIO

import matplotlib.pyplot as plt
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from services.interview_bank import InterviewBank
from services.learning_orchestrator import LearningOrchestrator
from services.progress_store import ProgressStore
from services.rag_store import LocalRAGStore


ACTIVITIES_FILE = Path("data/learning_activities.json")


def load_learning_activities() -> list[dict]:
    ACTIVITIES_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not ACTIVITIES_FILE.exists():
        ACTIVITIES_FILE.write_text("[]", encoding="utf-8")
    try:
        return json.loads(ACTIVITIES_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []


def save_learning_activities(items: list[dict]) -> None:
    ACTIVITIES_FILE.parent.mkdir(parents=True, exist_ok=True)
    ACTIVITIES_FILE.write_text(json.dumps(items, indent=2), encoding="utf-8")


def recommend_activities(goal: str, weak_topics: list[str], activities: list[dict], top_n: int = 3) -> list[dict]:
    if not activities:
        return []
    user_profile_text = f"{goal} {' '.join(weak_topics)}".strip()
    if not user_profile_text:
        return activities[:top_n]

    docs = [user_profile_text]
    docs.extend(
        [
            f"{item.get('title', '')} {item.get('category', '')} {item.get('notes', '')}"
            for item in activities
        ]
    )
    vectorizer = TfidfVectorizer(stop_words="english")
    matrix = vectorizer.fit_transform(docs)
    similarities = cosine_similarity(matrix[0:1], matrix[1:]).flatten()
    ranked_indices = similarities.argsort()[::-1][:top_n]
    return [activities[idx] for idx in ranked_indices]

st.markdown(
    """
    <style>
    /* Center the main chat column */
    .chat-main {
        max-width: 800px;
        margin: 0 auto;
    }

    /* Make system messages subtle */
    .chat-system {
        color: #888;
        font-size: 0.9rem;
        text-align: center;
        margin-bottom: 0.5rem;
    }

    /* Optional: tweak user/assistant bubbles via Streamlit's classes */
    .stChatMessage {
        max-width: 800px;
        margin-left: auto;
        margin-right: auto;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
st.set_page_config(page_title="AI Coach 2.0", layout="wide")
st.title("AI Coach 2.0")
st.caption("A focused AI learning workspace with guided practice and activity management.")

if "rag_store" not in st.session_state:
    st.session_state["rag_store"] = LocalRAGStore()
if "orchestrator" not in st.session_state:
    st.session_state["orchestrator"] = LearningOrchestrator(rag_store=st.session_state["rag_store"])
if "progress_store" not in st.session_state:
    st.session_state["progress_store"] = ProgressStore()
if "learning_history" not in st.session_state:
    st.session_state["learning_history"] = []
if "learning_activities" not in st.session_state:
    st.session_state["learning_activities"] = load_learning_activities()
if "interview_bank" not in st.session_state:
    st.session_state["interview_bank"] = InterviewBank()
    st.session_state["interview_bank"].seed_hot_roles()

orchestrator: LearningOrchestrator = st.session_state["orchestrator"]
progress_store: ProgressStore = st.session_state["progress_store"]
interview_bank: InterviewBank = st.session_state["interview_bank"]

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    ["Welcome", "AI Learning Studio", "Add Activities", "Learning Activities", "Progress", "Premium AI Lab"]
)

# --- TAB 1: Simple UI ---
with tab1:
    st.subheader("AI Learning Command Center")
    st.write("Set your learning signal, run an AI diagnostic, and get adaptive next actions.")

    profile_state = progress_store.read().get("profile", {})
    learner_name = st.text_input("Learner name", value=profile_state.get("name", ""))
    target_goal = st.text_input("Primary goal", value=profile_state.get("goal", ""))

    c1, c2, c3 = st.columns(3)
    with c1:
        python_conf = st.slider("Python confidence", 0, 100, 50)
    with c2:
        problem_solving = st.slider("Problem solving", 0, 100, 50)
    with c3:
        ai_skills = st.slider("AI Skills", 0, 100, 50)

    c4, c5, c6 = st.columns(3)
    with c4:
        consistency = st.slider("Consistency", 0, 100, 50)
    with c5:
        project_readiness = st.slider("Project readiness", 0, 100, 50)
    with c6:
        communication = st.slider("Communication", 0, 100, 50)
    speed = st.slider("Learning speed", 0, 100, 50)

    radar = go.Figure()
    radar.add_trace(
        go.Scatterpolar(
            r=[
                python_conf,
                problem_solving,
                ai_skills,
                consistency,
                project_readiness,
                communication,
                speed,
            ],
            theta=[
                "Python",
                "Problem Solving",
                "AI Skills",
                "Consistency",
                "Project",
                "Communication",
                "Speed",
            ],
            fill="toself",
            name="Skill Signal",
        )
    )
    radar.update_layout(
        polar={"radialaxis": {"visible": True, "range": [0, 100]}},
        showlegend=False,
        height=360,
        margin={"l": 20, "r": 20, "t": 20, "b": 20},
    )
    st.plotly_chart(radar, use_container_width=True)

    avg_score = int(
        (python_conf + problem_solving + ai_skills + consistency + project_readiness + communication + speed) / 7
    )
    s1, s2, s3 = st.columns(3)
    s1.metric("Learning Readiness", f"{avg_score}%")
    s2.metric("Top Strength", max(
        [
            ("Python", python_conf),
            ("Problem Solving", problem_solving),
            ("AI Skills", ai_skills),
            ("Consistency", consistency),
            ("Project", project_readiness),
            ("Communication", communication),
            ("Speed", speed),
        ],
        key=lambda item: item[1],
    )[0])
    s3.metric("Growth Priority", min(
        [
            ("Python", python_conf),
            ("Problem Solving", problem_solving),
            ("AI Skills", ai_skills),
            ("Consistency", consistency),
            ("Project", project_readiness),
            ("Communication", communication),
            ("Speed", speed),
        ],
        key=lambda item: item[1],
    )[0])

    if st.button("Generate AI Diagnostic & 7-Day Mission", type="primary"):
        if not target_goal.strip():
            st.error("Please add your primary goal.")
        else:
            diagnostic_prompt = (
                f"Learner: {learner_name or 'Learner'}\n"
                f"Goal: {target_goal}\n"
                "Scores:\n"
                f"- Python: {python_conf}\n"
                f"- Problem Solving: {problem_solving}\n"
                f"- AI Skills: {ai_skills}\n"
                f"- Consistency: {consistency}\n"
                f"- Project Readiness: {project_readiness}\n"
                f"- Communication: {communication}\n"
                f"- Learning Speed: {speed}\n\n"
                "Return: 1) diagnostic summary 2) key bottlenecks 3) 7-day mission plan."
            )
            with st.spinner("Building diagnostic..."):
                outcome = orchestrator.run(
                    mode="mentor",
                    user_input=diagnostic_prompt,
                    model=profile_state.get("preferred_model", "llama3.1"),
                    top_k=2,
                )
            st.write("### Personalized AI Diagnostic")
            st.markdown(outcome["raw_response"])
            progress_store.add_session_event("diagnostic", f"Generated diagnostic for: {target_goal}", xp_delta=20)


with tab2:
    st.subheader("AI Learning Studio")
    st.caption("Advanced modes for students and professionals. Running with local Ollama.")

    mode = st.selectbox(
        "Learning mode",
        options=["mentor", "quiz", "practice", "review", "planner"],
        format_func=lambda value: {
            "mentor": "Explain Like Mentor",
            "quiz": "Quiz Me",
            "practice": "Practice Problems",
            "review": "Project Review",
            "planner": "Study Plan Builder",
        }[value],
    )

    model_name = st.text_input("Ollama model", value="llama3.1")

    with st.expander("Upload learning material for contextual answers (RAG-lite)"):
        files = st.file_uploader(
            "Upload .txt, .md, or .csv files",
            type=["txt", "md", "csv"],
            accept_multiple_files=True,
        )
        if files:
            for file in files:
                chunks_added = st.session_state["rag_store"].add_document(file.name, file.read())
                st.success(f"Indexed {file.name} into {chunks_added} chunks")
        st.info(f"Current knowledge chunks: {st.session_state['rag_store'].chunk_count()}")

    prompt = st.text_area(
        "What do you want help with?",
        placeholder="Example: Help me master Python dictionaries in 2 weeks.",
        height=120,
    )
    top_k = st.slider("Context chunks to use", min_value=1, max_value=5, value=3)

    if st.button("Run AI Coach", type="primary"):
        if not prompt.strip():
            st.error("Please add a prompt.")
        else:
            with st.spinner("Generating..."):
                result = orchestrator.run(mode=mode, user_input=prompt, model=model_name, top_k=top_k)
            st.session_state["learning_history"].append(
                {"mode": mode, "prompt": prompt, "result": result}
            )

            st.write("### Coach Output")
            if result["parsed"] is not None:
                st.json(result["parsed"])
            else:
                st.markdown(result["raw_response"])

            if result["citations"]:
                st.write("### Sources Used")
                for citation in result["citations"]:
                    st.markdown(f"- `{citation['source_name']}` / `{citation['chunk_id']}`")

            if mode == "planner" and result["parsed"]:
                weekly_items = result["parsed"].get("weekly_plan", [])
                milestones = [item.get("milestone", "") for item in weekly_items if item.get("milestone")]
                if milestones:
                    progress_store.set_milestones(milestones)

            if mode == "quiz":
                quiz_topic = "general"
                if result["parsed"]:
                    quiz_topic = result["parsed"].get("topic", "general")
                # Placeholder metric until full grading flow is added.
                progress_store.add_quiz_result(topic=quiz_topic, score=0.7)
            progress_store.add_session_event("studio_run", f"Executed mode: {mode}", xp_delta=10)

    if st.session_state["learning_history"]:
        st.write("### Recent Learning Sessions")
        for item in reversed(st.session_state["learning_history"][-5:]):
            st.markdown(f"- **{item['mode']}**: {item['prompt'][:100]}")

with tab3:
    st.subheader("Add Activities")
    st.caption("Create, update, and delete your learning activities.")

    with st.form("create_activity_form", clear_on_submit=True):
        st.write("### Create")
        title = st.text_input("Activity title")
        category = st.selectbox("Category", ["Concept", "Practice", "Quiz", "Project", "Revision"])
        priority = st.selectbox("Priority", ["Low", "Medium", "High"])
        due_date = st.date_input("Due date")
        notes = st.text_area("Notes")
        create_clicked = st.form_submit_button("Create Activity")
        if create_clicked:
            if not title.strip():
                st.error("Title is required.")
            else:
                next_id = max([item.get("id", 0) for item in st.session_state["learning_activities"]] + [0]) + 1
                st.session_state["learning_activities"].append(
                    {
                        "id": next_id,
                        "title": title.strip(),
                        "category": category,
                        "priority": priority,
                        "due_date": str(due_date),
                        "status": "Open",
                        "notes": notes.strip(),
                    }
                )
                save_learning_activities(st.session_state["learning_activities"])
                st.success("Activity created.")

    activities = st.session_state["learning_activities"]
    if activities:
        st.write("### Update")
        activity_ids = [item["id"] for item in activities]
        selected_id = st.selectbox("Select activity ID", options=activity_ids)
        selected_item = next(item for item in activities if item["id"] == selected_id)

        with st.form("update_activity_form"):
            new_title = st.text_input("Title", value=selected_item["title"])
            new_status = st.selectbox(
                "Status",
                options=["Open", "In Progress", "Done"],
                index=["Open", "In Progress", "Done"].index(selected_item.get("status", "Open")),
            )
            new_priority = st.selectbox(
                "Priority",
                options=["Low", "Medium", "High"],
                index=["Low", "Medium", "High"].index(selected_item.get("priority", "Medium")),
            )
            new_notes = st.text_area("Notes", value=selected_item.get("notes", ""))
            update_clicked = st.form_submit_button("Update Activity")

            if update_clicked:
                for item in st.session_state["learning_activities"]:
                    if item["id"] == selected_id:
                        item["title"] = new_title.strip() or item["title"]
                        item["status"] = new_status
                        item["priority"] = new_priority
                        item["notes"] = new_notes.strip()
                        break
                save_learning_activities(st.session_state["learning_activities"])
                st.success("Activity updated.")

        st.write("### Delete")
        if st.button("Delete Selected Activity", type="secondary"):
            st.session_state["learning_activities"] = [
                item for item in st.session_state["learning_activities"] if item["id"] != selected_id
            ]
            save_learning_activities(st.session_state["learning_activities"])
            st.success("Activity deleted.")
            st.rerun()
    else:
        st.info("No activities available yet. Create one above.")

with tab4:
    st.subheader("Learning Activities Hub")
    st.write("Use these guided activities to practice consistently.")

    activities = st.session_state["learning_activities"]
    total_count = len(activities)
    done_count = sum(1 for item in activities if item.get("status") == "Done")
    open_count = total_count - done_count

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Activities", total_count)
    c2.metric("Completed", done_count)
    c3.metric("Open", open_count)

    st.write("### Suggested Weekly Activities")
    suggestions = [
        "Explain one concept in your own words (Feynman method)",
        "Solve 3 practice questions with increasing difficulty",
        "Take one mini quiz and review mistakes",
        "Build one tiny project artifact (script/notebook/summary)",
        "Run one project review and capture next actions",
    ]
    for idx, suggestion in enumerate(suggestions, start=1):
        st.markdown(f"{idx}. {suggestion}")

    if activities:
        st.write("### Current Activity Board")
        st.dataframe(pd.DataFrame(activities), use_container_width=True)

        profile = progress_store.read().get("profile", {})
        smart_items = recommend_activities(
            goal=profile.get("goal", ""),
            weak_topics=profile.get("weak_topics", []),
            activities=activities,
            top_n=3,
        )
        if smart_items:
            st.write("### AI Smart Recommendations")
            for idx, item in enumerate(smart_items, start=1):
                st.markdown(
                    f"{idx}. **{item.get('title', 'Untitled')}** "
                    f"({item.get('category', 'General')}, {item.get('priority', 'Medium')})"
                )
    else:
        st.info("No activities yet. Add one in the Add Activities tab.")

with tab5:
    st.subheader("Learning Profile & Progress Dashboard")
    state = progress_store.read()

    profile = state.get("profile", {})
    with st.form("profile_form"):
        goal = st.text_input("Learning goal", value=profile.get("goal", ""))
        level = st.selectbox(
            "Current level",
            ["beginner", "intermediate", "advanced"],
            index=["beginner", "intermediate", "advanced"].index(profile.get("level", "beginner")),
        )
        pace = st.slider("Hours per week", min_value=1, max_value=30, value=int(profile.get("pace_hours_per_week", 5)))
        weak_topics_text = st.text_input(
            "Weak topics (comma separated)",
            value=", ".join(profile.get("weak_topics", [])),
        )
        saved = st.form_submit_button("Save Profile")
        if saved:
            weak_topics = [topic.strip() for topic in weak_topics_text.split(",") if topic.strip()]
            progress_store.update_profile(
                {
                    "goal": goal,
                    "level": level,
                    "pace_hours_per_week": pace,
                    "weak_topics": weak_topics,
                }
            )
            st.success("Profile updated.")
            state = progress_store.read()

    st.write("### Quiz Trend")
    quiz_history = state.get("quiz_history", [])
    if quiz_history:
        quiz_df = pd.DataFrame(quiz_history)
        st.dataframe(quiz_df.tail(10), use_container_width=True)
        fig, ax = plt.subplots()
        ax.plot(range(len(quiz_df)), quiz_df["score"])
        ax.set_xlabel("Attempt")
        ax.set_ylabel("Score")
        ax.set_title("Recent Quiz Scores")
        st.pyplot(fig)
    else:
        st.info("No quiz attempts recorded yet.")

    st.write("### Upcoming Milestones")
    milestones = state.get("milestones", [])
    if milestones:
        for milestone in milestones:
            st.markdown(f"- {milestone}")
    else:
        st.info("No milestones yet. Use Study Plan Builder mode first.")

with tab6:
    st.subheader("Premium AI Lab")
    st.caption("Interview simulation, AI evaluator, gamification, and downloadable executive reporting.")

    engagement = progress_store.touch_daily_activity()
    xp_value = int(engagement.get("xp", 0))
    streak_value = int(engagement.get("streak_days", 0))
    level_value = max(1, xp_value // 120 + 1)
    k1, k2, k3 = st.columns(3)
    k1.metric("XP", xp_value)
    k2.metric("Daily Streak", streak_value)
    k3.metric("Learner Level", level_value)

    st.write("### AI Mock Interview Generator")
    interview_track = st.selectbox(
        "Track",
        ["Python Developer", "Data Analyst", "Machine Learning Engineer", "Backend Engineer"],
    )
    interview_difficulty = st.select_slider(
        "Interview difficulty",
        options=["Easy", "Medium", "Hard"],
        value="Medium",
    )
    if st.button("Generate Interview Questions"):
        interview_prompt = (
            f"Generate 5 {interview_difficulty} interview questions for {interview_track}. "
            "For each, add ideal answer points and one common mistake."
        )
        with st.spinner("Generating interview simulation..."):
            interview_out = orchestrator.run(
                mode="mentor",
                user_input=interview_prompt,
                model="llama3.1",
                top_k=1,
            )
        st.markdown(interview_out["raw_response"])
        progress_store.add_session_event(
            "interview_simulation",
            f"Generated {interview_difficulty} set for {interview_track}",
            xp_delta=15,
        )
        # Persist generated collection for later interview prep.
        interview_bank.add_question(
            position=interview_track,
            difficulty=interview_difficulty,
            question=f"Generated set for {interview_track} ({interview_difficulty})",
            ideal_points=interview_out["raw_response"][:3000],
            source="ai_generated",
        )

    st.write("### AI Answer Scoring Engine")
    eval_question = st.text_area("Question", placeholder="Paste interview question here.")
    eval_answer = st.text_area("Your answer", placeholder="Paste your answer for AI scoring.")
    if st.button("Score My Answer", type="primary"):
        if not eval_question.strip() or not eval_answer.strip():
            st.error("Please enter both question and answer.")
        else:
            evaluation_prompt = (
                "Evaluate the following answer.\n"
                f"Question: {eval_question}\n"
                f"Answer: {eval_answer}\n\n"
                "Return sections: score (0-10), strengths, weaknesses, improved answer, next drill."
            )
            with st.spinner("Scoring your answer..."):
                eval_out = orchestrator.run(
                    mode="review",
                    user_input=evaluation_prompt,
                    model="llama3.1",
                    top_k=1,
                )
            st.markdown(eval_out["raw_response"])
            progress_store.add_session_event("answer_scored", "Scored one user answer", xp_delta=25)

    st.write("### Download Executive Report")
    report_state = progress_store.read()
    report_profile = report_state.get("profile", {})
    report_quiz = report_state.get("quiz_history", [])[-10:]
    report_milestones = report_state.get("milestones", [])
    report_sessions = report_state.get("session_log", [])[-10:]

    report_buffer = StringIO()
    report_buffer.write("# LearnIQ Executive Learning Report\n\n")
    report_buffer.write("## Profile\n")
    report_buffer.write(f"- Goal: {report_profile.get('goal', '')}\n")
    report_buffer.write(f"- Level: {report_profile.get('level', 'beginner')}\n")
    report_buffer.write(f"- Pace: {report_profile.get('pace_hours_per_week', 5)} hrs/week\n")
    report_buffer.write(f"- Weak Topics: {', '.join(report_profile.get('weak_topics', []))}\n\n")
    report_buffer.write("## Engagement\n")
    report_buffer.write(f"- XP: {report_state.get('engagement', {}).get('xp', 0)}\n")
    report_buffer.write(f"- Streak: {report_state.get('engagement', {}).get('streak_days', 0)} days\n\n")
    report_buffer.write("## Quiz History\n")
    for row in report_quiz:
        report_buffer.write(f"- {row.get('topic', 'general')}: {row.get('score', 0)}\n")
    report_buffer.write("\n## Milestones\n")
    for milestone in report_milestones:
        report_buffer.write(f"- {milestone}\n")
    report_buffer.write("\n## Recent AI Sessions\n")
    for session in report_sessions:
        report_buffer.write(
            f"- [{session.get('timestamp', '')}] {session.get('event_type', '')}: {session.get('detail', '')}\n"
        )

    st.download_button(
        label="Download Report (.md)",
        data=report_buffer.getvalue().encode("utf-8"),
        file_name="learniq_executive_report.md",
        mime="text/markdown",
    )

    st.write("### Hot Positions Interview Collection (SQLite)")
    hot_positions = [
        "All",
        "AI Engineer",
        "Fullstack Engineer",
        "Backend Engineer",
        "Data Engineer",
        "ML Engineer",
        "DevOps Engineer",
        "Python Developer",
        "Data Analyst",
        "Machine Learning Engineer",
    ]
    selected_position = st.selectbox("Position filter", options=hot_positions)
    selected_difficulty = st.selectbox("Difficulty filter", options=["All", "Easy", "Medium", "Hard"])
    collection_rows = interview_bank.list_questions(
        position=selected_position,
        difficulty=selected_difficulty,
    )
    if collection_rows:
        collection_df = pd.DataFrame(collection_rows)
        st.dataframe(collection_df, use_container_width=True)
        st.download_button(
            label="Download Interview Collection (.csv)",
            data=collection_df.to_csv(index=False).encode("utf-8"),
            file_name="interview_collection.csv",
            mime="text/csv",
        )
    else:
        st.info("No interview questions found for this filter.")

st.markdown(
    """
    <div style="text-align: center; margin-top: 50px; color: #888;">
        © 2026 AI Coach 2.0 - SKcreation.org
    </div>
    """,
    unsafe_allow_html=True
)
