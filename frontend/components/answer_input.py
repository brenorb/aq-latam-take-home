"""Answer input component."""
import streamlit as st
from models.job import Job
from frontend.components.audio_recorder import render_audio_recorder
from frontend.services.transcription_service import process_audio_transcription
from frontend.services.interview_service import submit_answer_handler


def render_answer_input(job: Job, interview_state: dict) -> None:
    """
    Render the answer input area with audio recording, transcription, and text input.
    
    Args:
        job: The Job instance
        interview_state: Dictionary containing interview state
    """
    st.subheader("Your Answer")
    
    if interview_state["interview_started"] and not interview_state["interview_complete"]:
        # Display recording state
        recording_state = interview_state.get("recording_state", "idle")
        if recording_state == "recording":
            st.info("🎤 Recording...")
        elif recording_state == "processing":
            st.info("🔄 Transcribing...")
        elif recording_state == "submitting":
            st.info("📤 Submitting answer...")
        elif recording_state == "error":
            error_msg = interview_state.get("transcription_error", "Unknown error")
            st.error(f"❌ Error: {error_msg}")
        
        # Display transcribed text
        transcribed_text = interview_state.get("transcribed_text", "")
        if transcribed_text:
            if interview_state.get("debug_mode", False):
                # Debug mode: editable text area
                edited_text = st.text_area(
                    "Transcribed text (editable in debug mode):",
                    value=transcribed_text,
                    key=f"transcribed_text_{job.id}",
                    height=100
                )
                interview_state["transcribed_text"] = edited_text
                
                # Debug mode submit button
                if st.button("Submit Answer (Debug)", key=f"debug_submit_{job.id}"):
                    if edited_text.strip() and interview_state.get("session_id"):
                        submit_answer_handler(
                            interview_state["session_id"],
                            edited_text.strip(),
                            interview_state,
                            job.id
                        )
            else:
                # Normal mode: read-only display
                st.text_area(
                    "Transcribed text:",
                    value=transcribed_text,
                    key=f"transcribed_text_display_{job.id}",
                    height=100,
                    disabled=True
                )
        
        # Audio recorder component
        render_audio_recorder(job.id, interview_state.get("spacebar_enabled", True))
        
        # Audio file uploader
        uploaded_file = st.file_uploader(
            "Or upload an audio file",
            type=["webm", "wav", "mp3", "m4a"],
            key=f"audio_upload_{job.id}"
        )
        
        # Process uploaded audio file
        if uploaded_file is not None:
            process_audio_transcription(uploaded_file, job.id, interview_state)
        
        # Fallback text input form
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
                        session_id = interview_state.get("session_id")
                        if session_id:
                            submit_answer_handler(
                                session_id,
                                answer_text,
                                interview_state,
                                job.id
                            )
    elif not interview_state["interview_started"]:
        st.info("Start the interview to enable answer input")
    else:
        st.info("Interview complete - no more answers needed")

