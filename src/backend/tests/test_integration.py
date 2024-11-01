import pytest
import asyncio
from ..role_play_engine import RolePlayEngine


@pytest.mark.asyncio
async def test_full_session_flow(engine, user_id):
    """Test a complete session flow"""
    # Start session
    start_response = await engine.start_session(user_id)
    assert start_response["status"] == "success"
    assert "choices" in start_response

    # Process a choice
    choice_response = await engine.process_choice(user_id, "investigate")
    assert choice_response["status"] == "success"
    assert "content" in choice_response

    # Test input analysis
    analysis_response = await engine.analyze_input(
        user_id, "I want to explore the cave"
    )
    assert analysis_response["status"] == "success"


@pytest.mark.asyncio
async def test_concurrent_sessions(engine):
    """Test handling multiple concurrent sessions"""
    user_ids = [f"test_user_{i}" for i in range(3)]

    # Start multiple sessions concurrently
    responses = await asyncio.gather(
        *[engine.start_session(user_id) for user_id in user_ids]
    )

    assert all(r["status"] == "success" for r in responses)
    assert len(responses) == 3


@pytest.mark.asyncio
async def test_story_continuity(engine, user_id):
    """Test story continuity across choices"""
    await engine.start_session(user_id)

    # Make a series of choices
    choices = ["investigate", "continue", "wait"]
    story_segments = []

    for choice in choices:
        response = await engine.process_choice(user_id, choice)
        story_segments.append(response["content"])
        assert response["status"] == "success"

    assert len(story_segments) == len(choices)
