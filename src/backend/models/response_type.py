from enum import Enum


class ResponseType(Enum):
    SUCCESS = "success"
    ERROR = "error"
    STORY = "story"
    CHOICE = "choice"
    SYSTEM = "system"
    PROMPT = "prompt"
