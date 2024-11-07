import asyncio
import pytest
import pytest_asyncio
import os
import json
from pathlib import Path
from src.backend.role_play_engine import RolePlayEngine
from src.backend.models.response_type import ResponseType
from typing import Any, Generator, AsyncGenerator, Dict, List, Optional, Union


# Enable async test support
def pytest_configure(config: Any) -> None:
    """Configure test environment"""
    config.addinivalue_line("markers", "asyncio: mark test as async")


# Configure pytest-asyncio
def pytest_configure(config: Any) -> None:
    config.addinivalue_line("asyncio_mode", "strict")


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Set up test environment variables and configurations."""
    # Set test API key
    os.environ["API_KEY"] = "test_api_key"

    # Create test configurations
    config_dir = Path(__file__).parent.parent / "config"
    config_dir.mkdir(exist_ok=True)

    # Create test response templates
    response_templates = {
        "success": "Test: {message}",
        "error": "Error: {message}",
        "story": "Story: {content}\nChoices: {choices}",
    }

    with open(config_dir / "response_templates.json", "w") as f:
        json.dump(response_templates, f)

    yield

    # Cleanup
    if os.path.exists(config_dir / "response_templates.json"):
        os.remove(config_dir / "response_templates.json")


@pytest_asyncio.fixture
async def engine() -> AsyncGenerator[RolePlayEngine, None]:
    """Provide a test instance of RolePlayEngine."""
    engine = RolePlayEngine()
    await engine.initialize()
    yield engine  # This is what gets passed to the tests
    await engine.close()


@pytest.fixture
def user_id() -> str:
    """Provide a test user ID."""
    return "test_user_123"


# Mock API handler for testing
@pytest_asyncio.fixture
async def mock_api_handler():
    """Provide a mock API handler."""

    class MockAPIHandler:
        async def generate_story_content(self, *args, **kwargs):
            return {"content": "Test story content", "tokens_used": 10}

        async def analyze_user_input(self, *args, **kwargs):
            return {"analysis": "Test analysis"}

        async def close(self):
            pass

    return MockAPIHandler()


def pytest_configure(config: Any) -> None:
    config.addinivalue_line("markers", "integration: mark test as an integration test")


async def test_something(fixture: Any) -> None:
    pass
