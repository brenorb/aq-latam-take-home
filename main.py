"""Main Streamlit application for AI Interviewer Platform."""
import json
import streamlit as st
from models.job import Job, load_jobs
from api_client import start_interview, submit_answer, end_interview, get_session, get_evaluation, APIError


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
    
    Displays complete UI layout with text input area, AI question display,
    conversation history panel, and interview controls. Integrates with FastAPI
    backend for interview orchestration.
    
    Args:
        job: The selected Job instance to display
    """
    st.title(f"Interview Room: {job.title}")
    
    # Initialize interview state
    state_key = f"interview_state_{job.id}"
    if state_key not in st.session_state:
        st.session_state[state_key] = {
            "interview_started": False,
            "session_id": None,
            "conversation_history": [],
            "current_question": None,
            "question_number": 0,
            "interview_complete": False,
            "answer_text": "",
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
        elif interview_state["interview_complete"]:
            st.success("✅ Interview Complete!")
            st.info("Thank you for completing the interview. You can review the conversation history.")
        elif interview_state["current_question"]:
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
                    ">💬 {interview_state['current_question']}</h2>
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
        
        # Answer input area
        st.subheader("Your Answer")
        
        if interview_state["interview_started"] and not interview_state["interview_complete"]:
            # Microphone button (visual indicator only)
            st.info("🎤 Voice input coming soon - use text input below")
            
            # Use form for Enter key support and better UX
            with st.form(key=f"answer_form_{job.id}", clear_on_submit=True):
                # Text input for answers
                answer_text = st.text_area(
                    "Type your answer here... (Press Enter or Cmd+Enter to submit)",
                    value="",
                    key=f"answer_input_{job.id}",
                    height=150,
                    help="Press Enter or Cmd+Enter (Mac) / Ctrl+Enter (Windows) to submit"
                )
                
                # Form submit button (handles Enter key automatically)
                submitted = st.form_submit_button(
                    "Submit Answer",
                    type="primary",
                    use_container_width=True
                )
                
                # Add JavaScript for Cmd+Enter / Ctrl+Enter support
                # Note: Streamlit runs in iframe, so we need to access the parent frame
                st.components.v1.html(
                    f"""
                    <script>
                    (function() {{
                        function attachKeyboardHandler() {{
                            try {{
                                // Try to find textarea in current window first
                                let textarea = document.querySelector('textarea[placeholder*="Type your answer"]');
                                
                                // If not found, try parent window (for iframe)
                                if (!textarea && window.parent && window.parent !== window) {{
                                    textarea = window.parent.document.querySelector('textarea[placeholder*="Type your answer"]');
                                }}
                                
                                if (textarea && !textarea.dataset.cmdEnterHandler) {{
                                    textarea.dataset.cmdEnterHandler = 'true';
                                    textarea.addEventListener('keydown', function(e) {{
                                        if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {{
                                            e.preventDefault();
                                            // Find the form submit button
                                            const form = textarea.closest('form');
                                            if (form) {{
                                                const submitButton = form.querySelector('button[type="submit"], button[kind="formSubmit"]');
                                                if (submitButton) {{
                                                    submitButton.click();
                                                }}
                                            }}
                                        }}
                                    }});
                                }}
                            }} catch (err) {{
                                console.log('Keyboard handler setup:', err);
                            }}
                        }}
                        
                        // Try immediately and after a short delay (for dynamic content)
                        attachKeyboardHandler();
                        setTimeout(attachKeyboardHandler, 100);
                        setTimeout(attachKeyboardHandler, 500);
                    }})();
                    </script>
                    """,
                    height=0
                )
                
                if submitted:
                    # Check if interview is already complete
                    if interview_state["interview_complete"]:
                        st.warning("Interview is already complete. Cannot submit more answers.")
                    else:
                        answer_text = answer_text.strip() if answer_text else ""
                        if not answer_text:
                            st.warning("Please enter an answer before submitting.")
                        else:
                            try:
                                # Call API to submit answer
                                result = submit_answer(interview_state["session_id"], answer_text)
                                
                                # Sync conversation history from backend (single source of truth)
                                interview_state["conversation_history"] = result["conversation_history"]
                                
                                # Update state with next question
                                interview_state["current_question"] = result["question"]
                                interview_state["question_number"] = result["question_number"]
                                interview_state["interview_complete"] = result["interview_complete"]
                                
                                if result["interview_complete"]:
                                    st.success("Interview completed! Thank you for your responses.")
                                    # Store session_id for results page
                                    st.session_state["completed_session_id"] = interview_state["session_id"]
                                    st.session_state["completed_job_id"] = job.id
                                    # Navigate to results page
                                    st.session_state["current_page"] = "interview_results"
                                
                                # Rerun once to update UI or navigate
                                st.rerun()
                            except APIError as e:
                                st.error(f"Failed to submit answer: {str(e)}")
                            except Exception as e:
                                st.error(f"Unexpected error: {str(e)}")
        elif not interview_state["interview_started"]:
            st.info("Start the interview to enable answer input")
        else:
            st.info("Interview complete - no more answers needed")
    
    with col_right:
        # Conversation history panel
        st.subheader("Conversation History")
        
        conversation = interview_state["conversation_history"]
        if not conversation:
            st.info("No questions asked yet")
        else:
            # Display Q/A pairs in chronological order
            with st.container(height=400):
                for qa_pair in conversation:
                    st.markdown(f"**Q{qa_pair.get('question_number', '?')}:** {qa_pair['question']}")
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
                try:
                    # Call API to start interview
                    result = start_interview(job.id)
                    interview_state["interview_started"] = True
                    interview_state["session_id"] = result["session_id"]
                    interview_state["current_question"] = result["question"]
                    interview_state["question_number"] = result["question_number"]
                    interview_state["conversation_history"] = result.get("conversation_history", [])
                    interview_state["interview_complete"] = False
                    st.rerun()
                except APIError as e:
                    st.error(f"Failed to start interview: {str(e)}")
                except Exception as e:
                    st.error(f"Unexpected error: {str(e)}")
    
    with button_col2:
        # Submit Answer button moved inside form (handled above)
        # This column is kept for layout consistency but button is now in form
        pass
    
    with button_col3:
        # End Interview button (shown when interview is active)
        if interview_state["interview_started"]:
            if st.button("End Interview", type="secondary", use_container_width=True):
                try:
                    # Call API to end interview if session exists
                    if interview_state["session_id"]:
                        end_interview(interview_state["session_id"])
                        # Store session_id for results page
                        st.session_state["completed_session_id"] = interview_state["session_id"]
                        st.session_state["completed_job_id"] = job.id
                    
                    # Navigate to results page
                    st.session_state["current_page"] = "interview_results"
                    st.rerun()
                except APIError as e:
                    st.error(f"Failed to end interview: {str(e)}")
                except Exception as e:
                    st.error(f"Unexpected error: {str(e)}")
                    # Still try to navigate to results if session_id exists
                    if interview_state["session_id"]:
                        st.session_state["completed_session_id"] = interview_state["session_id"]
                        st.session_state["completed_job_id"] = job.id
                        st.session_state["current_page"] = "interview_results"
                    st.rerun()
    
    st.divider()
    
    # Action buttons for completed interview
    if interview_state["interview_complete"]:
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("View Results", type="primary", use_container_width=True):
                st.session_state["completed_session_id"] = interview_state["session_id"]
                st.session_state["completed_job_id"] = job.id
                st.session_state["current_page"] = "interview_results"
                st.rerun()
        with col2:
            if st.button("← Back to Job Listings", use_container_width=True):
                st.session_state["current_page"] = "job_listing"
                st.session_state["selected_job_id"] = None
                st.rerun()
    else:
        # Back button (when interview not complete)
        if st.button("← Back to Job Listings"):
            st.session_state["current_page"] = "job_listing"
            st.session_state["selected_job_id"] = None
            st.rerun()


def render_interview_results(session_id: str, job: Job) -> None:
    """
    Render the interview results page showing transcript and evaluation.
    
    Displays complete transcript of all Q/A pairs and structured evaluation
    with strengths, concerns, and overall score.
    
    Args:
        session_id: Session identifier
        job: The Job instance that was interviewed for
    """
    st.title(f"Interview Results: {job.title}")
    
    # Fetch session data
    try:
        with st.spinner("Loading session data..."):
            session_data = get_session(session_id)
    except APIError as e:
        st.error(f"Failed to load session: {str(e)}")
        if st.button("← Back to Job Listings"):
            st.session_state["current_page"] = "job_listing"
            st.session_state["selected_job_id"] = None
            st.rerun()
        return
    
    # Display session info
    st.info(f"**Session ID:** {session_id} | **Started:** {session_data.get('started_at', 'N/A')} | **Ended:** {session_data.get('ended_at', 'N/A')}")
    
    st.divider()
    
    # Transcript section
    st.header("📝 Interview Transcript")
    conversation_history = session_data.get("conversation_history", [])
    
    if not conversation_history:
        st.info("No conversation history available.")
    else:
        for entry in conversation_history:
            question_type = "Follow-up" if entry.get("is_followup") else "Standalone"
            st.markdown(f"**Q{entry.get('question_number', '?')}** ({question_type}):")
            st.markdown(f"*{entry.get('question', 'N/A')}*")
            st.markdown(f"**Answer:**")
            st.markdown(entry.get("answer", "N/A"))
            st.divider()
    
    st.divider()
    
    # Evaluation section
    st.header("📊 Evaluation")
    
    try:
        with st.spinner("Generating evaluation..."):
            evaluation = get_evaluation(session_id)
        
        # Overall score
        score = evaluation.get("overall_score", 0.0)
        st.metric("Overall Score", f"{score:.1f}/100")
        
        # Strengths
        strengths = evaluation.get("strengths", [])
        if strengths:
            st.subheader("✅ Strengths")
            for strength in strengths:
                st.markdown(f"- {strength}")
        else:
            st.info("No specific strengths identified.")
        
        st.divider()
        
        # Concerns
        concerns = evaluation.get("concerns", [])
        if concerns:
            st.subheader("⚠️ Areas for Improvement")
            for concern in concerns:
                st.markdown(f"- {concern}")
        else:
            st.info("No specific concerns identified.")
        
        # Raw JSON (expandable)
        with st.expander("View Raw Evaluation JSON"):
            st.json(evaluation)
            
    except APIError as e:
        st.error(f"Failed to generate evaluation: {str(e)}")
        st.info("Transcript is still available above.")
    
    st.divider()
    
    # Back button
    if st.button("← Back to Job Listings", type="primary"):
        st.session_state["current_page"] = "job_listing"
        st.session_state["selected_job_id"] = None
        st.session_state["completed_session_id"] = None
        st.session_state["completed_job_id"] = None
        st.rerun()


def main() -> None:
    """
    Main application entry point.
    
    Initializes Streamlit session state for navigation and job selection,
    loads job data from JSON file, and routes to the appropriate page based
    on the current session state.
    
    Session state keys:
        current_page: Either "job_listing", "interview_room", or "interview_results"
        selected_job_id: ID of the currently selected job (None if none selected)
        completed_session_id: Session ID of completed interview (for results page)
        completed_job_id: Job ID of completed interview (for results page)
    """
    # Initialize session state
    if "current_page" not in st.session_state:
        st.session_state["current_page"] = "job_listing"
    if "selected_job_id" not in st.session_state:
        st.session_state["selected_job_id"] = None
    if "completed_session_id" not in st.session_state:
        st.session_state["completed_session_id"] = None
    if "completed_job_id" not in st.session_state:
        st.session_state["completed_job_id"] = None
    
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
    elif st.session_state["current_page"] == "interview_results":
        # Find job for completed session
        completed_job_id = st.session_state.get("completed_job_id")
        completed_session_id = st.session_state.get("completed_session_id")
        
        if not completed_session_id:
            st.error("No session ID provided. Returning to job listings.")
            st.session_state["current_page"] = "job_listing"
            st.rerun()
            return
        
        completed_job = next(
            (job for job in jobs if job.id == completed_job_id),
            None
        )
        
        if completed_job:
            render_interview_results(completed_session_id, completed_job)
        else:
            st.error("Job not found. Returning to job listings.")
            st.session_state["current_page"] = "job_listing"
            st.session_state["completed_session_id"] = None
            st.session_state["completed_job_id"] = None
            st.rerun()


if __name__ == "__main__":
    main()
