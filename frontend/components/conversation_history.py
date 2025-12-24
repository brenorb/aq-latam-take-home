"""Conversation history component."""
import streamlit as st


def render_conversation_history(conversation: list[dict]) -> None:
    """
    Render the conversation history panel.
    
    Args:
        conversation: List of Q/A pair dictionaries
    """
    st.subheader("Conversation History")
    
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

