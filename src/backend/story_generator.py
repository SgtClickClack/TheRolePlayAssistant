from typing import Dict, List, Optional
import json
import os
from pathlib import Path


class StoryGenerator:
    def __init__(self):
        self.prompts = self._load_prompts()
        self.current_story = None
        self.story_state = {}
        self.story_templates = self._load_story_templates()
        self.story_flow = {
            "start": {
                "choices": [
                    {"id": "investigate", "text": "Investigate further"},
                    {"id": "retreat", "text": "Retreat carefully"},
                    {"id": "explore", "text": "Explore the surroundings"}
                ]
            },
            "investigate": {
                "choices": [
                    {"id": "continue", "text": "Continue investigating"},
                    {"id": "hide", "text": "Find a hiding spot"},
                    {"id": "run", "text": "Run away quickly"}
                ]
            },
            "hide": {
                "choices": [
                    {"id": "wait", "text": "Wait and observe"},
                    {"id": "emerge", "text": "Emerge from hiding"},
                    {"id": "move_stealthily", "text": "Move stealthily"}
                ]
            },
            "continue": {
                "choices": [
                    {"id": "wait", "text": "Wait and observe"},
                    {"id": "proceed", "text": "Proceed carefully"},
                    {"id": "retreat", "text": "Retreat"}
                ]
            }
        }

    def _load_prompts(self) -> dict:
        """Load story prompts from JSON configuration file"""
        prompts_path = Path(__file__).parent / "config" / "prompts.json"
        try:
            with open(prompts_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            # Fallback to default prompts if file doesn't exist
            return {
                "intro": {
                    "template": "You find yourself in {setting}. {initial_situation}",
                    "variables": {
                        "setting": [
                            "a mysterious forest",
                            "an ancient temple",
                            "a futuristic city",
                        ],
                        "initial_situation": [
                            "The air is thick with anticipation.",
                            "Something feels different today.",
                            "You sense an adventure beginning.",
                        ],
                    },
                },
                "conflict": {
                    "template": "Suddenly, {event} occurs. You must {action}.",
                    "variables": {
                        "event": [
                            "a strange noise",
                            "an unexpected visitor",
                            "a mysterious light",
                        ],
                        "action": [
                            "investigate carefully",
                            "make a quick decision",
                            "prepare for danger",
                        ],
                    },
                },
            }

    def _load_story_templates(self) -> dict:
        """Load story structure templates"""
        return {
            "basic": {
                "intro": self.prompts["intro"],
                "conflict": self.prompts["conflict"],
                "choices": [
                    {"id": "investigate", "text": "Investigate further"},
                    {"id": "retreat", "text": "Retreat carefully"},
                    {"id": "explore", "text": "Explore the surroundings"},
                ],
            }
        }

    async def generate_story_segment(self, context: Dict) -> Dict:
        """
        Generate next story segment based on context
        Returns dict containing story text and available choices
        """
        try:
            # If this is the start of the story
            if not self.current_story:
                template = self.story_templates["basic"]["intro"]
                story_text = self._generate_from_template(template)
                choices = self.story_templates["basic"]["choices"]

                self.current_story = {
                    "current_node": "intro",
                    "story_text": story_text,
                    "choices": choices,
                }

                return self.current_story

            # If continuing existing story
            choice = context.get("choice")
            if choice:
                return await self._generate_next_segment(choice)

            raise ValueError("No choice provided for story continuation")

        except Exception as e:
            return {
                "error": f"Failed to generate story segment: {str(e)}",
                "choices": [],
            }

    def _generate_from_template(self, template_data: Dict) -> str:
        """Generate text from template with random variables"""
        import random

        base_template = template_data["template"]
        variables = template_data["variables"]

        # Replace each variable with random choice from its options
        replacements = {
            key: random.choice(options) for key, options in variables.items()
        }

        return base_template.format(**replacements)

    async def _generate_next_segment(self, choice: str) -> Dict:
        """Generate next story segment based on player choice"""
        # Map choices to consequences
        choice_consequences = {
            "start": {
                "template": self.story_templates["basic"]["intro"],
                "choices": [
                    {"id": "investigate", "text": "Investigate further"},
                    {"id": "retreat", "text": "Retreat carefully"},
                    {"id": "explore", "text": "Explore the surroundings"}
                ]
            },
            "investigate": {
                "template": self.story_templates["basic"]["conflict"],
                "choices": [
                    {"id": "fight", "text": "Stand and fight"},
                    {"id": "hide", "text": "Find a hiding spot"},
                    {"id": "run", "text": "Run away quickly"},
                ],
            },
            "retreat": {
                "template": {
                    "template": "You carefully back away. {consequence}",
                    "variables": {
                        "consequence": [
                            "The mystery remains unsolved.",
                            "You hear distant sounds fading.",
                            "Safety comes at the cost of adventure.",
                        ]
                    },
                },
                "choices": [
                    {"id": "return", "text": "Return cautiously"},
                    {"id": "leave", "text": "Leave the area"},
                    {"id": "observe", "text": "Observe from afar"},
                ],
            },
            "explore": {
                "template": {
                    "template": "You decide to explore the area. {discovery}",
                    "variables": {
                        "discovery": [
                            "You stumble upon a hidden cave.",
                            "You find a strange artifact on the ground.",
                            "You notice footprints leading deeper into the forest.",
                        ]
                    },
                },
                "choices": [
                    {"id": "enter_cave", "text": "Enter the cave"},
                    {"id": "examine_artifact", "text": "Examine the artifact"},
                    {"id": "follow_footprints", "text": "Follow the footprints"},
                ],
            },
            "wait": {
                "template": {
                    "template": "You decide to wait. {event}",
                    "variables": {
                        "event": [
                            "Nothing happens for a while.",
                            "You hear distant sounds approaching.",
                            "A feeling of unease settles in.",
                        ]
                    },
                },
                "choices": [
                    {"id": "investigate", "text": "Investigate the sound"},
                    {"id": "retreat", "text": "Retreat to a safer place"},
                    {"id": "stand_guard", "text": "Stand guard and stay alert"},
                ],
            },
            "run": {
                "template": {
                    "template": "You run as fast as you can. {outcome}",
                    "variables": {
                        "outcome": [
                            "You escape safely.",
                            "You stumble but regain your footing.",
                            "You run into another challenge.",
                        ]
                    },
                },
                "choices": [
                    {"id": "rest", "text": "Take a moment to rest"},
                    {"id": "continue_running", "text": "Keep running"},
                    {"id": "hide", "text": "Find a place to hide"},
                ],
            },
            "hide": {
                "template": {
                    "template": "You find a hiding spot. {event}",
                    "variables": {
                        "event": [
                            "You wait until it's safe.",
                            "You overhear something interesting.",
                            "You realize you're not alone.",
                        ]
                    },
                },
                "choices": [
                    {"id": "emerge", "text": "Emerge from hiding"},
                    {"id": "stay_hidden", "text": "Stay hidden longer"},
                    {"id": "move_stealthily", "text": "Move stealthily"},
                ],
            },
        }

        if choice not in choice_consequences:
            raise ValueError(f"Invalid choice: {choice}")

        consequence = choice_consequences[choice]
        story_text = self._generate_from_template(consequence["template"])

        self.current_story = {
            "current_node": choice,
            "story_text": story_text,
            "choices": consequence["choices"],
        }

        return self.current_story

    def get_initial_choices(self) -> List[Dict[str, str]]:
        """Get initial choices for a new story"""
        return [
            {"id": "explore", "text": "Explore the surroundings"},
            {"id": "talk", "text": "Talk to someone nearby"},
            {"id": "wait", "text": "Wait and observe"},
        ]

    def get_valid_choices(self, last_choice: str) -> List[Dict[str, str]]:
        """Get valid choices based on the last choice made"""
        return self.story_flow.get(last_choice, {}).get("choices", [])
