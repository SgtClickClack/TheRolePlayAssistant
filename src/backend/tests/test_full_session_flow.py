async def test_full_session_flow(engine, user_id):
    # First, start the session
    await engine.start_session(user_id)
    
    # Then process the choice
    choice_response = await engine.process_choice(user_id, "investigate")
    assert choice_response["status"] == "success"
    assert "choices" in choice_response

    # Process next choice
    next_choice_response = await engine.process_choice(user_id, "continue")
    assert next_choice_response["status"] == "success"
    assert "choices" in next_choice_response
    ... 