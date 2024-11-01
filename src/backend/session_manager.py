from datetime import datetime, timedelta
from typing import Dict, Optional, List
import uuid
import json
from pathlib import Path


class SessionManager:
    def __init__(self):
        self.active_sessions: Dict[str, dict] = {}
        self.session_timeout = timedelta(hours=2)  # Sessions expire after 2 hours
        self.max_sessions_per_user = 3
        self.session_directory = Path(__file__).parent / "data" / "sessions"

        # Create sessions directory if it doesn't exist
        self.session_directory.mkdir(parents=True, exist_ok=True)

    def create_session(self, user_id: str) -> dict:
        """
        Create new roleplay session
        Returns session data including ID and initial state
        """
        # Clean expired sessions first
        self._clean_expired_sessions()

        # Check if user has too many active sessions
        user_sessions = self.get_user_sessions(user_id)
        if len(user_sessions) >= self.max_sessions_per_user:
            raise ValueError(
                f"User has reached maximum session limit of {self.max_sessions_per_user}"
            )

        session_id = str(uuid.uuid4())
        timestamp = datetime.now()

        session_data = {
            "session_id": session_id,
            "user_id": user_id,
            "start_time": timestamp.isoformat(),
            "last_activity": timestamp.isoformat(),
            "story_state": {},
            "user_choices": [],
            "status": "active",
        }

        self.active_sessions[session_id] = session_data
        self._save_session(session_id, session_data)

        return session_data

    def get_session(self, session_id: str) -> Optional[dict]:
        """Retrieve session by ID"""
        session = self.active_sessions.get(session_id)

        if not session:
            # Try to load from disk
            session = self._load_session(session_id)
            if session:
                self.active_sessions[session_id] = session

        if session and not self._is_session_expired(session):
            self._update_last_activity(session_id)
            return session

        return None

    def update_session(self, session_id: str, updates: dict) -> dict:
        """Update session with new data"""
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found or expired")

        session.update(updates)
        session["last_activity"] = datetime.now().isoformat()

        self._save_session(session_id, session)
        return session

    def end_session(self, session_id: str) -> bool:
        """End session and archive its data"""
        session = self.get_session(session_id)
        if not session:
            return False

        session["status"] = "completed"
        session["end_time"] = datetime.now().isoformat()

        self._save_session(session_id, session)
        self.active_sessions.pop(session_id, None)

        return True

    def get_user_sessions(self, user_id: str) -> List[dict]:
        """Get all active sessions for a user"""
        return [
            session
            for session in self.active_sessions.values()
            if session["user_id"] == user_id and not self._is_session_expired(session)
        ]

    def _is_session_expired(self, session: dict) -> bool:
        """Check if session has expired"""
        last_activity = datetime.fromisoformat(session["last_activity"])
        return datetime.now() - last_activity > self.session_timeout

    def _update_last_activity(self, session_id: str) -> None:
        """Update last activity timestamp"""
        if session_id in self.active_sessions:
            self.active_sessions[session_id][
                "last_activity"
            ] = datetime.now().isoformat()
            self._save_session(session_id, self.active_sessions[session_id])

    def _clean_expired_sessions(self) -> None:
        """Remove expired sessions from memory"""
        expired = [
            session_id
            for session_id, session in self.active_sessions.items()
            if self._is_session_expired(session)
        ]

        for session_id in expired:
            self.active_sessions.pop(session_id, None)

    def _save_session(self, session_id: str, session_data: dict) -> None:
        """Save session data to disk"""
        try:
            file_path = self.session_directory / f"{session_id}.json"
            with open(file_path, "w") as f:
                json.dump(session_data, f, indent=2)
        except Exception as e:
            print(f"Error saving session {session_id}: {e}")

    def _load_session(self, session_id: str) -> Optional[dict]:
        """Load session data from disk"""
        try:
            file_path = self.session_directory / f"{session_id}.json"
            if file_path.exists():
                with open(file_path, "r") as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading session {session_id}: {e}")
        return None

    def get_session_history(self, session_id: str) -> List[dict]:
        """Get chronological history of session choices and events"""
        session = self.get_session(session_id)
        if not session:
            return []
        return session.get("user_choices", [])

    def add_to_session_history(self, session_id: str, event: dict) -> bool:
        """Add new event to session history"""
        session = self.get_session(session_id)
        if not session:
            return False

        event["timestamp"] = datetime.now().isoformat()
        session["user_choices"].append(event)
        self._save_session(session_id, session)
        return True
