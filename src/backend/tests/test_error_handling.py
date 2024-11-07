import pytest
from typing import Any
from src.backend.models.response_type import ResponseType

# Engine fixture is automatically available from conftest.py


@pytest.mark.asyncio
async def test_error_scenarios(engine: Any) -> None:
    """Test error handling when an invalid session ID is provided"""
    # Expect a ValueError when using an invalid session ID
    with pytest.raises(ValueError) as exc_info:
        await engine.process_choice("invalid_id", "explore")
    assert str(exc_info.value) == "Invalid session ID"
