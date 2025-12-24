"""Question display component."""
import streamlit as st


def render_question_display(interview_state: dict) -> None:
    """
    Render the current question display area.
    
    Args:
        interview_state: Dictionary containing interview state
    """
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

