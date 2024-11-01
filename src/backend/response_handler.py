from typing import Dict, Any, Optional, Union, List
from datetime import datetime
import json
from pathlib import Path
from enum import Enum


class ResponseType(Enum):
    SUCCESS = "success"
    ERROR = "error"
    STORY = "story"
    CHOICE = "choice"
    SYSTEM = "system"
    PROMPT = "prompt"


class ResponseHandler:
    def __init__(self):
        self.templates = self._load_templates()
        self.fallback_templates = {
            ResponseType.ERROR.value: "An error occurred: {message}",
            ResponseType.SUCCESS.value: "{message}",
            ResponseType.STORY.value: "{content}\n\nChoices:\n{choices}",
            ResponseType.CHOICE.value: "You chose: {choice}",
            ResponseType.SYSTEM.value: "System: {message}",
            ResponseType.PROMPT.value: "What would you like to do?\n{options}",
        }

    def _load_templates(self) -> Dict[str, str]:
        """Load response templates from configuration file"""
        template_path = Path(__file__).parent / "config" / "response_templates.json"
        try:
            with open(template_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return self.fallback_templates

    def format_response(
        self,
        response_type: Union[ResponseType, str],
        data: Dict[str, Any],
        metadata: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Format response using appropriate template"""
        if isinstance(response_type, ResponseType):
            response_type = response_type.value

        template = self.templates.get(
            response_type, self.fallback_templates.get(response_type)
        )

        if not template:
            raise ValueError(f"Unknown response type: {response_type}")

        try:
            formatted_content = template.format(**data)

            response = {
                "type": response_type,
                "content": formatted_content,
                "timestamp": datetime.now().isoformat(),
            }

            if metadata:
                response["metadata"] = metadata

            return response

        except KeyError as e:
            return self.format_error(f"Missing required data field: {e}")
        except Exception as e:
            return self.format_error(f"Error formatting response: {e}")

    def format_story_response(
        self, story_content: str, choices: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """Format a story response with choices"""
        formatted_choices = "\n".join(
            f"{i+1}. {choice['text']}" for i, choice in enumerate(choices)
        )

        return self.format_response(
            ResponseType.STORY,
            {"content": story_content, "choices": formatted_choices},
            metadata={
                "choice_count": len(choices),
                "choice_ids": [choice.get("id") for choice in choices],
            },
        )

    def format_error(
        self, message: str, details: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Format an error response"""
        response = self.format_response(ResponseType.ERROR, {"message": message})

        if details:
            response["error_details"] = details

        return response

    def format_success(
        self, message: str, data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Format a success response"""
        response = self.format_response(ResponseType.SUCCESS, {"message": message})

        if data:
            response["data"] = data

        return response

    def format_prompt(
        self, prompt_text: str, options: List[str], context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Format a prompt response with options"""
        formatted_options = "\n".join(f"- {option}" for option in options)

        return self.format_response(
            ResponseType.PROMPT,
            {"options": formatted_options},
            metadata={"prompt_text": prompt_text, "context": context},
        )

    def format_system_message(
        self, message: str, level: str = "info"
    ) -> Dict[str, Any]:
        """Format a system message"""
        return self.format_response(
            ResponseType.SYSTEM, {"message": message}, metadata={"level": level}
        )

    def validate_response(self, response: Dict[str, Any]) -> bool:
        """Validate response structure"""
        required_fields = {"type", "content", "timestamp"}
        return all(field in response for field in required_fields)

    def enrich_response(
        self, response: Dict[str, Any], enrichment_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Enrich response with additional data"""
        enriched = response.copy()

        if "metadata" not in enriched:
            enriched["metadata"] = {}

        enriched["metadata"].update(enrichment_data)

        return enriched
