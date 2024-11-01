import os
import aiohttp
import asyncio
import json
import time
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime
from aiohttp import ClientSession


class APIHandler:
    def __init__(self) -> None:
        # Load configuration
        self.config = self._load_config()

        # API endpoints and keys
        self.base_url = os.getenv("API_BASE_URL", self.config.get("base_url"))
        self.api_key = os.getenv("API_KEY", self.config.get("api_key"))

        # Rate limiting settings
        self.rate_limit = self.config.get("rate_limit", 60)  # requests per minute
        self.request_history: List[float] = []

        # Retry settings
        self.max_retries = 3
        self.retry_delay = 1  # seconds

        # Initialize session pool
        self.session: Optional[ClientSession] = None

    async def initialize(self) -> None:
        """Initialize the API handler"""
        if self.session is None:
            self.session = aiohttp.ClientSession(
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                }
            )

    async def close(self) -> None:
        """Close the API session"""
        if self.session:
            await self.session.close()
            self.session = None

    def _load_config(self) -> dict:
        """Load API configuration from file"""
        config_path = Path(__file__).parent / "config" / "api_config.json"
        try:
            with open(config_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "base_url": "https://api.openai.com/v1",
                "rate_limit": 60,
                "endpoints": {
                    "completion": "/completions",
                    "chat": "/chat/completions",
                },
                "models": {"default": "gpt-3.5-turbo", "advanced": "gpt-4"},
            }

    def _check_rate_limit(self) -> bool:
        """Check if we're within rate limits"""
        current_time = time.time()
        # Remove requests older than 1 minute
        self.request_history = [
            t for t in self.request_history if current_time - t < 60
        ]

        return len(self.request_history) < self.rate_limit

    async def _make_request(
        self, endpoint: str, payload: Dict, method: str = "POST"
    ) -> Dict:
        """Make HTTP request with retry logic"""
        if self.session is None:
            await self.initialize()

        for attempt in range(self.max_retries):
            try:
                if not self._check_rate_limit():
                    raise Exception("Rate limit exceeded")

                self.request_history.append(time.time())

                async with self.session.request(
                    method, f"{self.base_url}{endpoint}", json=payload
                ) as response:
                    if response.status == 429:  # Too Many Requests
                        retry_after = int(
                            response.headers.get("Retry-After", self.retry_delay)
                        )
                        await asyncio.sleep(retry_after)
                        continue

                    response.raise_for_status()
                    return await response.json()

            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise
                await asyncio.sleep(self.retry_delay * (attempt + 1))

        raise Exception("Max retries exceeded")

    async def generate_story_content(
        self, prompt: str, context: Optional[Dict] = None
    ) -> Dict:
        """Generate story content using AI model"""
        payload = {
            "model": self.config["models"]["default"],
            "messages": [
                {"role": "system", "content": "You are a creative storyteller."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.7,
            "max_tokens": 500,
        }

        if context:
            payload["messages"].insert(
                1,
                {
                    "role": "system",
                    "content": f"Previous context: {json.dumps(context)}",
                },
            )

        try:
            response = await self._make_request(
                self.config["endpoints"]["chat"], payload
            )

            return {
                "content": response["choices"][0]["message"]["content"],
                "tokens_used": response["usage"]["total_tokens"],
                "model": response["model"],
            }

        except Exception as e:
            return {"error": str(e), "content": None}

    async def analyze_user_input(
        self, user_input: str, context: Optional[Dict] = None
    ) -> Dict:
        """Analyze user input for sentiment and intent"""
        payload = {
            "model": self.config["models"]["default"],
            "messages": [
                {
                    "role": "system",
                    "content": "Analyze the following user input for sentiment and intent.",
                },
                {"role": "user", "content": user_input},
            ],
        }

        try:
            response = await self._make_request(
                self.config["endpoints"]["chat"], payload
            )

            return {
                "analysis": response["choices"][0]["message"]["content"],
                "tokens_used": response["usage"]["total_tokens"],
            }

        except Exception as e:
            return {"error": str(e), "analysis": None}

    def log_api_interaction(self, endpoint: str, success: bool, details: Dict) -> None:
        """Log API interactions for monitoring"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "endpoint": endpoint,
            "success": success,
            "details": details,
        }

        log_path = Path(__file__).parent / "logs" / "api_interactions.jsonl"
        log_path.parent.mkdir(exist_ok=True)

        with open(log_path, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
