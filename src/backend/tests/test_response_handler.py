import pytest
from src.backend.response_handler import ResponseHandler, ResponseType


@pytest.fixture
def handler():
    return ResponseHandler()


def test_basic_response_formatting(handler):
    response = handler.format_response(
        ResponseType.SUCCESS, {"message": "Test successful"}
    )

    assert response["type"] == "success"
    assert "Test successful" in response["content"]
    assert "timestamp" in response


def test_story_response_formatting(handler):
    story_content = "You enter a dark cave."
    choices = [
        {"id": "enter", "text": "Go deeper"},
        {"id": "leave", "text": "Return outside"},
    ]

    response = handler.format_story_response(story_content, choices)

    assert response["type"] == "story"
    assert "dark cave" in response["content"]
    assert "Go deeper" in response["content"]
    assert "Return outside" in response["content"]
    assert response["metadata"]["choice_count"] == 2


def test_error_handling(handler):
    response = handler.format_error("Something went wrong")

    assert response["type"] == "error"
    assert "Something went wrong" in response["content"]


def test_response_validation(handler):
    valid_response = {
        "type": "success",
        "content": "Test",
        "timestamp": "2024-03-20T12:00:00",
    }

    assert handler.validate_response(valid_response)

    invalid_response = {"type": "success", "content": "Test"}

    assert not handler.validate_response(invalid_response)
