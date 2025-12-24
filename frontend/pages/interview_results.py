"""Interview results page."""
import streamlit as st
from models.job import Job
from api_client import get_session, get_evaluation, APIError


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

