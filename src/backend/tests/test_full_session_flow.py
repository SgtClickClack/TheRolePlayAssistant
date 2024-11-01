async def test_full_session_flow(engine, user_id):
    # First, start the session
    session_response = await engine.start_session(user_id)
    assert session_response["status"] == "success"  # Verify session started successfully
    
    # Then process the choice
    choice_response = await engine.process_choice(user_id, "investigate")
    assert choice_response["status"] == "success"
    assert "choices" in choice_response
    assert isinstance(choice_response["choices"], list)  # Verify choices is a list

    # Process next choice
    next_choice_response = await engine.process_choice(user_id, "continue")
    assert next_choice_response["status"] == "success"
    assert "choices" in next_choice_response
    assert isinstance(next_choice_response["choices"], list)
    ... 