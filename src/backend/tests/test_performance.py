import pytest
import asyncio
import time

# Engine fixture is automatically available from conftest.py


@pytest.mark.asyncio
async def test_concurrent_sessions(engine):
    """Test handling multiple sessions"""
    start_time = time.time()
    user_count = 5
    user_ids = [f"perf_user_{i}" for i in range(user_count)]

    # Test concurrent session creation
    responses = await asyncio.gather(
        *[engine.start_session(user_id) for user_id in user_ids]
    )

    assert len(responses) == user_count
    assert all(r["status"] == "success" for r in responses)

    # Test concurrent choice processing
    choice_responses = await asyncio.gather(
        *[engine.process_choice(user_id, "investigate") for user_id in user_ids]
    )

    assert len(choice_responses) == user_count
    assert all(r["status"] == "success" for r in choice_responses)

    end_time = time.time()
    assert end_time - start_time < 2.0  # Performance threshold


@pytest.mark.asyncio
async def test_response_time(engine, user_id):
    """Test individual operation response times"""
    # Test session start time
    start_time = time.time()
    await engine.start_session(user_id)
    session_time = time.time() - start_time
    assert session_time < 0.5  # 500ms threshold

    # Test choice processing time
    start_time = time.time()
    await engine.process_choice(user_id, "investigate")
    choice_time = time.time() - start_time
    assert choice_time < 0.5  # 500ms threshold
