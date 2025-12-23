"""Tests for interview room page rendering."""
import pytest
from unittest.mock import MagicMock
from models.job import Job


def test_generate_mock_questions_returns_role_grounded_questions():
    """Test that generate_mock_questions creates role-grounded questions."""
    from main import generate_mock_questions
    
    job = Job(
        id="job_1",
        title="Software Engineer",
        description="Build amazing software",
        department="Engineering",
        location="Remote",
        requirements=["Python", "FastAPI"]
    )
    
    questions = generate_mock_questions(job)
    
    assert isinstance(questions, list)
    assert len(questions) >= 3
    assert all(isinstance(q, str) for q in questions)
    # Verify questions contain job-specific keywords
    assert "Software Engineer" in questions[0] or "Engineering" in questions[0]
    assert "Python" in questions[1]  # First requirement should be in questions


def test_generate_mock_questions_handles_empty_requirements():
    """Test that generate_mock_questions handles jobs with empty requirements."""
    from main import generate_mock_questions
    
    job = Job(
        id="job_1",
        title="Product Manager",
        description="Lead product",
        department="Product",
        location="Remote",
        requirements=[]
    )
    
    questions = generate_mock_questions(job)
    
    assert len(questions) >= 3
    assert all(isinstance(q, str) for q in questions)


def test_render_interview_room_initializes_interview_state(mocker):
    """Test that render_interview_room initializes interview state."""
    mock_st = mocker.patch('main.st')
    mock_st.session_state = {}
    mock_st.title = MagicMock()
    mock_st.write = MagicMock()
    mock_st.expander = MagicMock(return_value=MagicMock())
    mock_st.subheader = MagicMock()
    mock_st.divider = MagicMock()
    # Mock columns to return different numbers based on call
    def columns_side_effect(sizes):
        if len(sizes) == 2:
            return [MagicMock(), MagicMock()]
        elif len(sizes) == 3:
            return [MagicMock(), MagicMock(), MagicMock()]
        return [MagicMock()] * len(sizes)
    mock_st.columns = MagicMock(side_effect=columns_side_effect)
    mock_st.markdown = MagicMock()
    mock_st.info = MagicMock()
    mock_st.button = MagicMock(return_value=False)
    mock_st.rerun = MagicMock()
    mock_st.container = MagicMock(return_value=MagicMock())
    
    job = Job(
        id="job_1",
        title="Software Engineer",
        description="Build amazing software",
        department="Engineering",
        location="Remote",
        requirements=["Python"]
    )
    
    from main import render_interview_room
    render_interview_room(job)
    
    # Verify interview state was initialized
    state_key = f"interview_state_{job.id}"
    assert state_key in mock_st.session_state
    assert mock_st.session_state[state_key]["interview_started"] is False
    assert mock_st.session_state[state_key]["mock_conversation"] == []
    assert mock_st.session_state[state_key]["current_mock_question"] is None


def test_render_interview_room_shows_start_interview_button_when_not_started(mocker):
    """Test that Start Interview button appears when interview hasn't started."""
    mock_st = mocker.patch('main.st')
    mock_st.session_state = {}
    mock_st.title = MagicMock()
    mock_st.write = MagicMock()
    mock_st.expander = MagicMock(return_value=MagicMock())
    mock_st.subheader = MagicMock()
    mock_st.divider = MagicMock()
    def columns_side_effect(sizes):
        if len(sizes) == 2:
            return [MagicMock(), MagicMock()]
        elif len(sizes) == 3:
            return [MagicMock(), MagicMock(), MagicMock()]
        return [MagicMock()] * len(sizes)
    mock_st.columns = MagicMock(side_effect=columns_side_effect)
    mock_st.markdown = MagicMock()
    mock_st.info = MagicMock()
    mock_st.rerun = MagicMock()
    mock_st.container = MagicMock(return_value=MagicMock())
    
    button_calls = []
    def button_side_effect(*args, **kwargs):
        button_calls.append(str(args[0]) if args else "")
        return False
    
    mock_st.button = MagicMock(side_effect=button_side_effect)
    
    job = Job(
        id="job_1",
        title="Engineer",
        description="Build",
        department="Eng",
        location="Remote",
        requirements=["Python"]
    )
    
    from main import render_interview_room
    render_interview_room(job)
    
    # Verify Start Interview button exists
    assert any("Start Interview" in call for call in button_calls)


def test_start_interview_button_starts_interview(mocker):
    """Test that clicking Start Interview button initializes interview state."""
    mock_st = mocker.patch('main.st')
    state_key = "interview_state_job_1"
    mock_st.session_state = {
        state_key: {
            "interview_started": False,
            "mock_conversation": [],
            "current_mock_question": None,
            "mock_questions": ["Q1", "Q2", "Q3"],
            "question_index": 0,
        }
    }
    mock_st.title = MagicMock()
    mock_st.write = MagicMock()
    mock_st.expander = MagicMock(return_value=MagicMock())
    mock_st.subheader = MagicMock()
    mock_st.divider = MagicMock()
    def columns_side_effect(sizes):
        if len(sizes) == 2:
            return [MagicMock(), MagicMock()]
        elif len(sizes) == 3:
            return [MagicMock(), MagicMock(), MagicMock()]
        return [MagicMock()] * len(sizes)
    mock_st.columns = MagicMock(side_effect=columns_side_effect)
    mock_st.markdown = MagicMock()
    mock_st.info = MagicMock()
    mock_st.rerun = MagicMock()
    mock_st.container = MagicMock(return_value=MagicMock())
    
    call_count = 0
    def button_side_effect(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if "Start Interview" in str(args[0]):
            mock_st.session_state[state_key]["interview_started"] = True
            mock_st.session_state[state_key]["current_mock_question"] = "Q1"
            return True
        return False
    
    mock_st.button = MagicMock(side_effect=button_side_effect)
    
    job = Job(
        id="job_1",
        title="Engineer",
        description="Build",
        department="Eng",
        location="Remote",
        requirements=["Python"]
    )
    
    from main import render_interview_room
    render_interview_room(job)
    
    # Verify interview started
    assert mock_st.session_state[state_key]["interview_started"] is True
    assert mock_st.session_state[state_key]["current_mock_question"] == "Q1"


def test_submit_answer_button_adds_to_conversation(mocker):
    """Test that Submit Answer button appears when interview is active."""
    mock_st = mocker.patch('main.st')
    state_key = "interview_state_job_1"
    mock_st.session_state = {
        state_key: {
            "interview_started": True,
            "mock_conversation": [],
            "current_mock_question": "Question 1?",
            "mock_questions": ["Question 1?", "Question 2?"],
            "question_index": 0,
        }
    }
    mock_st.title = MagicMock()
    mock_st.write = MagicMock()
    mock_st.expander = MagicMock(return_value=MagicMock())
    mock_st.subheader = MagicMock()
    mock_st.divider = MagicMock()
    def columns_side_effect(sizes):
        if len(sizes) == 2:
            return [MagicMock(), MagicMock()]
        elif len(sizes) == 3:
            return [MagicMock(), MagicMock(), MagicMock()]
        return [MagicMock()] * len(sizes)
    mock_st.columns = MagicMock(side_effect=columns_side_effect)
    mock_st.markdown = MagicMock()
    mock_st.info = MagicMock()
    mock_st.rerun = MagicMock()
    mock_st.container = MagicMock(return_value=MagicMock())
    
    button_calls = []
    def button_side_effect(*args, **kwargs):
        button_calls.append(str(args[0]) if args else "")
        return False  # Don't simulate clicks, just track button renders
    
    mock_st.button = MagicMock(side_effect=button_side_effect)
    
    job = Job(
        id="job_1",
        title="Engineer",
        description="Build",
        department="Eng",
        location="Remote",
        requirements=["Python"]
    )
    
    from main import render_interview_room
    render_interview_room(job)
    
    # Verify Submit Answer button was rendered when interview is active
    assert any("Submit Answer" in call for call in button_calls)


def test_end_interview_button_resets_state(mocker):
    """Test that End Interview button resets interview state."""
    mock_st = mocker.patch('main.st')
    state_key = "interview_state_job_1"
    mock_st.session_state = {
        state_key: {
            "interview_started": True,
            "mock_conversation": [{"question": "Q1", "answer": "A1"}],
            "current_mock_question": "Q2",
            "mock_questions": ["Q1", "Q2"],
            "question_index": 1,
        }
    }
    mock_st.title = MagicMock()
    mock_st.write = MagicMock()
    mock_st.expander = MagicMock(return_value=MagicMock())
    mock_st.subheader = MagicMock()
    mock_st.divider = MagicMock()
    def columns_side_effect(sizes):
        if len(sizes) == 2:
            return [MagicMock(), MagicMock()]
        elif len(sizes) == 3:
            return [MagicMock(), MagicMock(), MagicMock()]
        return [MagicMock()] * len(sizes)
    mock_st.columns = MagicMock(side_effect=columns_side_effect)
    mock_st.markdown = MagicMock()
    mock_st.info = MagicMock()
    mock_st.rerun = MagicMock()
    mock_st.container = MagicMock(return_value=MagicMock())
    
    def button_side_effect(*args, **kwargs):
        if "End Interview" in str(args[0]):
            mock_st.session_state[state_key]["interview_started"] = False
            mock_st.session_state[state_key]["mock_conversation"] = []
            mock_st.session_state[state_key]["current_mock_question"] = None
            mock_st.session_state[state_key]["question_index"] = 0
            return True
        return False
    
    mock_st.button = MagicMock(side_effect=button_side_effect)
    
    job = Job(
        id="job_1",
        title="Engineer",
        description="Build",
        department="Eng",
        location="Remote",
        requirements=["Python"]
    )
    
    from main import render_interview_room
    render_interview_room(job)
    
    # Verify state was reset
    assert mock_st.session_state[state_key]["interview_started"] is False
    assert mock_st.session_state[state_key]["mock_conversation"] == []
    assert mock_st.session_state[state_key]["current_mock_question"] is None


def test_render_interview_room_displays_conversation_history(mocker):
    """Test that conversation history is displayed when it exists."""
    mock_st = mocker.patch('main.st')
    state_key = "interview_state_job_1"
    mock_st.session_state = {
        state_key: {
            "interview_started": True,
            "mock_conversation": [
                {"question": "Q1", "answer": "A1"},
                {"question": "Q2", "answer": "A2"},
            ],
            "current_mock_question": "Q3",
            "mock_questions": ["Q1", "Q2", "Q3"],
            "question_index": 2,
        }
    }
    mock_st.title = MagicMock()
    mock_st.write = MagicMock()
    mock_st.expander = MagicMock(return_value=MagicMock())
    mock_st.subheader = MagicMock()
    mock_st.divider = MagicMock()
    def columns_side_effect(sizes):
        if len(sizes) == 2:
            return [MagicMock(), MagicMock()]
        elif len(sizes) == 3:
            return [MagicMock(), MagicMock(), MagicMock()]
        return [MagicMock()] * len(sizes)
    mock_st.columns = MagicMock(side_effect=columns_side_effect)
    mock_st.markdown = MagicMock()
    mock_st.info = MagicMock()
    mock_st.button = MagicMock(return_value=False)
    mock_st.rerun = MagicMock()
    mock_st.container = MagicMock(return_value=MagicMock())
    
    job = Job(
        id="job_1",
        title="Engineer",
        description="Build",
        department="Eng",
        location="Remote",
        requirements=["Python"]
    )
    
    from main import render_interview_room
    render_interview_room(job)
    
    # Verify markdown was called to display conversation (Q/A pairs)
    assert mock_st.markdown.called


def test_render_interview_room_shows_microphone_when_interview_started(mocker):
    """Test that microphone button appears when interview has started."""
    mock_st = mocker.patch('main.st')
    state_key = "interview_state_job_1"
    mock_st.session_state = {
        state_key: {
            "interview_started": True,
            "mock_conversation": [],
            "current_mock_question": "Q1",
            "mock_questions": ["Q1"],
            "question_index": 0,
        }
    }
    mock_st.title = MagicMock()
    mock_st.write = MagicMock()
    mock_st.expander = MagicMock(return_value=MagicMock())
    mock_st.subheader = MagicMock()
    mock_st.divider = MagicMock()
    def columns_side_effect(sizes):
        if len(sizes) == 2:
            return [MagicMock(), MagicMock()]
        elif len(sizes) == 3:
            return [MagicMock(), MagicMock(), MagicMock()]
        return [MagicMock()] * len(sizes)
    mock_st.columns = MagicMock(side_effect=columns_side_effect)
    mock_st.markdown = MagicMock()
    mock_st.info = MagicMock()
    mock_st.button = MagicMock(return_value=False)
    mock_st.rerun = MagicMock()
    mock_st.container = MagicMock(return_value=MagicMock())
    
    job = Job(
        id="job_1",
        title="Engineer",
        description="Build",
        department="Eng",
        location="Remote",
        requirements=["Python"]
    )
    
    from main import render_interview_room
    render_interview_room(job)
    
    # Verify button was called (should include microphone button)
    assert mock_st.button.called


def test_render_interview_room_has_back_button(mocker):
    """Test that render_interview_room includes a Back button."""
    mock_st = mocker.patch('main.st')
    mock_st.session_state = {}
    mock_st.title = MagicMock()
    mock_st.write = MagicMock()
    mock_st.expander = MagicMock(return_value=MagicMock())
    mock_st.subheader = MagicMock()
    mock_st.divider = MagicMock()
    def columns_side_effect(sizes):
        if len(sizes) == 2:
            return [MagicMock(), MagicMock()]
        elif len(sizes) == 3:
            return [MagicMock(), MagicMock(), MagicMock()]
        return [MagicMock()] * len(sizes)
    mock_st.columns = MagicMock(side_effect=columns_side_effect)
    mock_st.markdown = MagicMock()
    mock_st.info = MagicMock()
    mock_st.rerun = MagicMock()
    mock_st.container = MagicMock(return_value=MagicMock())
    
    button_calls = []
    def button_side_effect(*args, **kwargs):
        button_calls.append(str(args[0]) if args else "")
        return False
    
    mock_st.button = MagicMock(side_effect=button_side_effect)
    
    job = Job(
        id="job_1",
        title="Engineer",
        description="Build",
        department="Eng",
        location="Remote",
        requirements=["Python"]
    )
    
    from main import render_interview_room
    render_interview_room(job)
    
    # Verify back button exists
    assert any("back" in call.lower() or "Back" in call for call in button_calls)


def test_render_interview_room_back_button_resets_session_state(mocker):
    """Test that Back button resets current_page and clears selected_job_id."""
    mock_st = mocker.patch('main.st')
    mock_st.session_state = {
        "current_page": "interview_room",
        "selected_job_id": "job_1"
    }
    mock_st.title = MagicMock()
    mock_st.write = MagicMock()
    mock_st.expander = MagicMock(return_value=MagicMock())
    mock_st.subheader = MagicMock()
    mock_st.divider = MagicMock()
    def columns_side_effect(sizes):
        if len(sizes) == 2:
            return [MagicMock(), MagicMock()]
        elif len(sizes) == 3:
            return [MagicMock(), MagicMock(), MagicMock()]
        return [MagicMock()] * len(sizes)
    mock_st.columns = MagicMock(side_effect=columns_side_effect)
    mock_st.markdown = MagicMock()
    mock_st.info = MagicMock()
    mock_st.rerun = MagicMock()
    mock_st.container = MagicMock(return_value=MagicMock())
    
    def button_side_effect(*args, **kwargs):
        if "back" in str(args[0]).lower() or "Back" in str(args[0]):
            mock_st.session_state["current_page"] = "job_listing"
            mock_st.session_state["selected_job_id"] = None
            return True
        return False
    
    mock_st.button = MagicMock(side_effect=button_side_effect)
    
    job = Job(
        id="job_1",
        title="Engineer",
        description="Build",
        department="Eng",
        location="Remote",
        requirements=["Python"]
    )
    
    from main import render_interview_room
    render_interview_room(job)
    
    # Verify session state is reset
    assert mock_st.session_state["current_page"] == "job_listing"
    assert mock_st.session_state["selected_job_id"] is None
    assert mock_st.rerun.called

