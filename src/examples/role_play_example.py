import asyncio
from backend.role_play_engine import RolePlayEngine


async def main():
    # Initialize the engine
    engine = RolePlayEngine()
    await engine.initialize()

    try:
        # Start a new session
        start_response = await engine.start_session("user123")
        print("Session Started:", start_response)

        # Get the session ID from the response
        session_id = start_response.get("metadata", {}).get("session_id")

        # Make a choice
        choice_response = await engine.process_choice(session_id, "explore")
        print("\nChoice Made:", choice_response)

        # Process some free-form input
        input_response = await engine.analyze_free_input(
            session_id, "I want to search for hidden treasures"
        )
        print("\nFree Input Response:", input_response)

        # Get session summary
        summary = engine.get_session_summary(session_id)
        print("\nSession Summary:", summary)

    finally:
        # Clean up
        await engine.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
