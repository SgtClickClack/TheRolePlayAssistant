import pytest
import asyncio
from src.backend.session_manager import SessionManager


@pytest.mark.asyncio
async def test_session_lifecycle(engine, user_id):
    """Test session creation, management and cleanup"""
    # Create session
    session = await engine.start_session(user_id)
    assert session["status"] == "success"

    # Verify session exists
    response = await engine.process_choice(user_id, "investigate")
    assert response["status"] == "success"

    # Clean up
    await engine.close()

    # Verify session is cleaned up
    with pytest.raises(ValueError):
        await engine.process_choice(user_id, "investigate")


@pytest.mark.asyncio
async def test_session_state(engine, user_id):
    """Test session state management"""
    # Add debug logging
    session_response = await engine.start_session(user_id)
    print(f"Session created with response: {session_response}")  # Debug
    print(f"Engine sessions before choices: {engine.sessions}")  # Updated debug message
    
    # Verify session was actually stored
    assert user_id in engine.sessions, "Session was not stored in engine.sessions"
    
    # Make several choices and verify state persistence
    choices = ["investigate", "hide", "wait"]
    for choice in choices:
        response = await engine.process_choice(user_id, choice)
        print(f"Response after choice '{choice}': {response}")  # Additional debug
        assert response["status"] == "success"


@pytest.mark.asyncio
async def test_multiple_sessions(engine):
    """Test multiple session handling"""
    session_count = 3
    sessions = []

    # Create multiple sessions
    for i in range(session_count):
        response = await engine.start_session(f"multi_user_{i}")
        sessions.append(response)

    assert len(sessions) == session_count
    assert all(s["status"] == "success" for s in sessions)
