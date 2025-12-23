"""Main Streamlit application for AI Interviewer Platform."""
import json
import streamlit as st
from models.job import Job, load_jobs


def generate_mock_questions(job: Job) -> list[str]:
    """
    Generate role-grounded mock questions for the selected job.
    
    Creates a list of interview questions that reflect the job's title,
    department, and requirements. Questions are hardcoded templates that
    incorporate job-specific keywords.
    
    Args:
        job: The Job instance to generate questions for
        
    Returns:
        List of 3-4 role-grounded interview questions
    """
    # Extract job-specific keywords
    title_lower = job.title.lower()
    dept_lower = job.department.lower()
    
    # Get first requirement as example skill
    first_skill = job.requirements[0] if job.requirements else "this role"
    
    # Generate role-grounded questions
    questions = [
        f"Why are you interested in this {job.title} position in {job.department}?",
        f"Tell me about your experience with {first_skill}.",
        f"Describe a project where you demonstrated skills relevant to {job.title}.",
        f"What challenges have you faced in {dept_lower}, and how did you overcome them?",
    ]
    
    return questions


def render_job_listing(jobs: list[Job]) -> None:
    """
    Render the job listing page displaying all available positions.
    
    Shows each job's title, department, location, description, and requirements.
    Each job has a button to start an interview, which navigates to the interview room.
    
    Args:
        jobs: List of Job instances to display
    """
    st.title("Available Positions")
    st.write("Select a job to start your interview:")
    
    for job in jobs:
        with st.container():
            st.subheader(job.title)
            st.write(f"**Department:** {job.department}")
            st.write(f"**Location:** {job.location}")
            st.write(f"**Description:** {job.description}")
            st.write(f"**Requirements:** {', '.join(job.requirements)}")
            
            if st.button(f"Start Interview - {job.title}", key=f"job_{job.id}"):
                st.session_state["selected_job_id"] = job.id
                st.session_state["current_page"] = "interview_room"
                st.rerun()


def render_interview_room(job: Job) -> None:
    """
    Render the interview room page for the selected job.
    
    Displays complete UI layout with microphone input area, AI question display,
    conversation history panel, and interview controls. Includes mock question
    generation and simulated conversation flow.
    
    Args:
        job: The selected Job instance to display
    """
    st.title(f"Interview Room: {job.title}")
    
    # Initialize interview state
    state_key = f"interview_state_{job.id}"
    if state_key not in st.session_state:
        st.session_state[state_key] = {
            "interview_started": False,
            "mock_conversation": [],
            "current_mock_question": None,
            "mock_questions": generate_mock_questions(job),
            "question_index": 0,
        }
    
    interview_state = st.session_state[state_key]
    
    # Job information (compact display)
    with st.expander("Job Details", expanded=False):
        st.write(f"**Department:** {job.department}")
        st.write(f"**Location:** {job.location}")
        st.write(f"**Description:** {job.description}")
        st.write(f"**Requirements:** {', '.join(job.requirements)}")
    
    st.divider()
    
    # Main interview area - two column layout
    col_left, col_right = st.columns([7, 3])
    
    with col_left:
        # Question display area
        st.subheader("Current Question")
        
        if not interview_state["interview_started"]:
            st.info("Click 'Start Interview' to begin")
        elif interview_state["current_mock_question"]:
            # Display question prominently - larger and more distinct than regular info boxes
            st.markdown(
                f"""
                <div style="
                    background-color: #f0f2f6;
                    padding: 24px;
                    border-radius: 8px;
                    border-left: 4px solid #ff4b4b;
                    margin: 16px 0;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                ">
                    <h2 style="
                        color: #262730;
                        font-size: 1.5rem;
                        font-weight: 600;
                        margin: 0;
                        line-height: 1.4;
                    ">💬 {interview_state['current_mock_question']}</h2>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.caption("Please provide your answer below")
        elif interview_state["interview_started"]:
            # Interview started but no question - should not happen, but handle gracefully
            st.warning("Loading question...")
        else:
            st.info("No question available")
        
        st.divider()
        
        # Answer input area with microphone
        st.subheader("Your Answer")
        
        if interview_state["interview_started"]:
            # Microphone button (visual only)
            mic_col1, mic_col2 = st.columns([3, 1])
            with mic_col1:
                if st.button("🎤 Click to Record", key="mic_button", use_container_width=True):
                    # Visual feedback only - no actual audio capture
                    st.info("Microphone button clicked (visual only - no audio capture yet)")
            with mic_col2:
                st.write("")  # Spacing
        else:
            st.info("Start the interview to enable microphone input")
    
    with col_right:
        # Conversation history panel
        st.subheader("Conversation History")
        
        conversation = interview_state["mock_conversation"]
        if not conversation:
            st.info("No questions asked yet")
        else:
            # Display Q/A pairs in chronological order
            with st.container(height=400):
                for qa_pair in conversation:
                    st.markdown(f"**Q:** {qa_pair['question']}")
                    answer_text = qa_pair.get("answer", "Waiting for answer...")
                    st.markdown(f"**A:** {answer_text}")
                    st.divider()
    
    st.divider()
    
    # Action buttons section
    button_col1, button_col2, button_col3 = st.columns([1, 1, 1])
    
    with button_col1:
        # Start Interview button (shown when interview hasn't started)
        if not interview_state["interview_started"]:
            if st.button("Start Interview", type="primary", use_container_width=True):
                # Start the interview and set the first question immediately
                interview_state["interview_started"] = True
                interview_state["question_index"] = 0
                # Ensure first question is set when interview starts - this must happen before rerun
                if not interview_state.get("mock_questions"):
                    interview_state["mock_questions"] = generate_mock_questions(job)
                # Always set the first question when starting
                interview_state["current_mock_question"] = interview_state["mock_questions"][0]
                st.rerun()
    
    with button_col2:
        # Answer Question button (shown when interview is active)
        if interview_state["interview_started"] and interview_state["current_mock_question"]:
            if st.button("Submit Answer", type="primary", use_container_width=True):
                # Simulate adding answer to conversation
                current_q = interview_state["current_mock_question"]
                interview_state["mock_conversation"].append({
                    "question": current_q,
                    "answer": "Sample answer demonstrating the conversation flow...",
                })
                
                # Move to next question
                interview_state["question_index"] += 1
                questions = interview_state["mock_questions"]
                if interview_state["question_index"] < len(questions):
                    interview_state["current_mock_question"] = questions[interview_state["question_index"]]
                else:
                    interview_state["current_mock_question"] = None
                    st.info("All mock questions completed!")
                
                st.rerun()
    
    with button_col3:
        # End Interview button (shown when interview is active)
        if interview_state["interview_started"]:
            if st.button("End Interview", type="secondary", use_container_width=True):
                # Reset interview state
                interview_state["interview_started"] = False
                interview_state["mock_conversation"] = []
                interview_state["current_mock_question"] = None
                interview_state["question_index"] = 0
                st.rerun()
    
    st.divider()
    
    # Back button
    if st.button("← Back to Job Listings"):
        st.session_state["current_page"] = "job_listing"
        st.session_state["selected_job_id"] = None
        st.rerun()


def main() -> None:
    """
    Main application entry point.
    
    Initializes Streamlit session state for navigation and job selection,
    loads job data from JSON file, and routes to the appropriate page based
    on the current session state.
    
    Session state keys:
        current_page: Either "job_listing" or "interview_room"
        selected_job_id: ID of the currently selected job (None if none selected)
    """
    # Initialize session state
    if "current_page" not in st.session_state:
        st.session_state["current_page"] = "job_listing"
    if "selected_job_id" not in st.session_state:
        st.session_state["selected_job_id"] = None
    
    # Load jobs
    try:
        jobs = load_jobs()
    except FileNotFoundError:
        st.error("Jobs data file not found. Please ensure data/jobs.json exists.")
        return
    except json.JSONDecodeError as e:
        st.error(f"Invalid JSON in jobs data file: {e}")
        return
    except (ValueError, TypeError) as e:
        st.error(f"Error loading jobs data: {e}")
        return
    
    # Route to appropriate page
    if st.session_state["current_page"] == "job_listing":
        render_job_listing(jobs)
    elif st.session_state["current_page"] == "interview_room":
        # Find selected job
        selected_job = next(
            (job for job in jobs if job.id == st.session_state["selected_job_id"]),
            None
        )
        if selected_job:
            render_interview_room(selected_job)
        else:
            st.error("Job not found. Returning to job listings.")
            st.session_state["current_page"] = "job_listing"
            st.session_state["selected_job_id"] = None
            st.rerun()


if __name__ == "__main__":
    main()
