"""Audio recorder component."""
import streamlit as st


def render_audio_recorder(job_id: str, spacebar_enabled: bool) -> None:
    """
    Render audio recorder component with MediaRecorder API and spacebar hotkey support.
    
    Args:
        job_id: Job ID for unique element IDs
        spacebar_enabled: Whether spacebar hotkey is enabled
    """
    # Convert Python boolean to JavaScript boolean string
    spacebar_enabled_js = "true" if spacebar_enabled else "false"
    
    st.components.v1.html(
        f"""
        <div id="audio-recorder-{job_id}">
            <button id="record-btn-{job_id}" style="padding: 10px 20px; margin: 10px;">
                🎤 Start Recording
            </button>
            <button id="stop-btn-{job_id}" style="padding: 10px 20px; margin: 10px; display: none;">
                ⏹ Stop Recording
            </button>
            <div id="recording-status-{job_id}" style="margin: 10px;"></div>
            <audio id="audio-playback-{job_id}" controls style="display: none; margin: 10px;"></audio>
            <a id="download-link-{job_id}" style="display: none; margin: 10px;">Download Audio</a>
        </div>
        <script>
        (function() {{
            const jobId = "{job_id}";
            const spacebarEnabled = {spacebar_enabled_js};
            let mediaRecorder = null;
            let audioChunks = [];
            let stream = null;
            
            const recordBtn = document.getElementById(`record-btn-${{jobId}}`);
            const stopBtn = document.getElementById(`stop-btn-${{jobId}}`);
            const statusDiv = document.getElementById(`recording-status-${{jobId}}`);
            const audioPlayback = document.getElementById(`audio-playback-${{jobId}}`);
            const downloadLink = document.getElementById(`download-link-${{jobId}}`);
            
            function updateStatus(message) {{
                statusDiv.textContent = message;
            }}
            
            async function startRecording() {{
                try {{
                    stream = await navigator.mediaDevices.getUserMedia({{ audio: true }});
                    mediaRecorder = new MediaRecorder(stream);
                    audioChunks = [];
                    
                    mediaRecorder.ondataavailable = (event) => {{
                        audioChunks.push(event.data);
                    }};
                    
                    mediaRecorder.onstop = () => {{
                        const audioBlob = new Blob(audioChunks, {{ type: 'audio/webm' }});
                        const audioUrl = URL.createObjectURL(audioBlob);
                        audioPlayback.src = audioUrl;
                        audioPlayback.style.display = 'block';
                        
                        // Create download link
                        downloadLink.href = audioUrl;
                        downloadLink.download = `audio-${{jobId}}.webm`;
                        downloadLink.style.display = 'block';
                        
                        // Store blob in window for Streamlit to access
                        window[`audioBlob_${{jobId}}`] = audioBlob;
                        
                        updateStatus("Recording stopped. Download the audio file and upload it.");
                    }};
                    
                    mediaRecorder.start();
                    recordBtn.style.display = 'none';
                    stopBtn.style.display = 'inline-block';
                    updateStatus("Recording... Press spacebar to stop (if enabled)");
                }} catch (error) {{
                    updateStatus(`Error: ${{error.message}}`);
                }}
            }}
            
            function stopRecording() {{
                if (mediaRecorder && mediaRecorder.state !== 'inactive') {{
                    mediaRecorder.stop();
                    stream.getTracks().forEach(track => track.stop());
                    recordBtn.style.display = 'inline-block';
                    stopBtn.style.display = 'none';
                }}
            }}
            
            recordBtn.addEventListener('click', startRecording);
            stopBtn.addEventListener('click', stopRecording);
            
            // Spacebar hotkey support
            if (spacebarEnabled) {{
                let spacebarPressed = false;
                
                document.addEventListener('keydown', (e) => {{
                    if (e.code === 'Space' && !spacebarPressed) {{
                        e.preventDefault();
                        spacebarPressed = true;
                        if (!mediaRecorder || mediaRecorder.state === 'inactive') {{
                            startRecording();
                        }}
                    }}
                }});
                
                document.addEventListener('keyup', (e) => {{
                    if (e.code === 'Space' && spacebarPressed) {{
                        e.preventDefault();
                        spacebarPressed = false;
                        if (mediaRecorder && mediaRecorder.state === 'recording') {{
                            stopRecording();
                        }}
                    }}
                }});
            }}
        }})();
        </script>
        """,
        height=200
    )

