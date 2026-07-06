"""In-memory conversation storage for the CityPulse hybrid assistant."""

from collections import deque
from dataclasses import dataclass, field
from datetime import UTC, datetime
from threading import Lock
from uuid import uuid4

from app.models.intent import IntentType


MAX_MESSAGES_PER_SESSION = 20


@dataclass(frozen=True)
class ConversationMessage:
    """A single stored assistant conversation turn."""

    role: str
    content: str
    timestamp: str
    intent: IntentType | None = None


@dataclass
class ConversationSession:
    """A bounded in-memory conversation session."""

    session_id: str
    messages: deque[ConversationMessage] = field(
        default_factory=lambda: deque(maxlen=MAX_MESSAGES_PER_SESSION)
    )


class ConversationMemory:
    """Thread-safe in-memory conversation store.

    This is intentionally process-local. It is suitable for local development
    and early milestone validation, and can be replaced by Redis or a database
    without changing the assistant endpoint contract.
    """

    def __init__(self) -> None:
        """Initialize an empty conversation memory store."""
        self._sessions: dict[str, ConversationSession] = {}
        self._lock = Lock()

    def get_or_create_session(self, session_id: str | None = None) -> str:
        """Return an existing session ID or create a new session.

        Args:
            session_id: Optional caller-provided session identifier.

        Returns:
            A valid session ID.

        Raises:
            ValueError: If the provided session ID is blank.
        """
        normalized_session_id = self._normalize_session_id(session_id)

        with self._lock:
            if normalized_session_id is None:
                normalized_session_id = str(uuid4())

            self._sessions.setdefault(
                normalized_session_id,
                ConversationSession(session_id=normalized_session_id),
            )

        return normalized_session_id

    def add_user_message(self, session_id: str, content: str) -> None:
        """Store a user message in a conversation session."""
        self._add_message(
            session_id=session_id,
            message=ConversationMessage(
                role="user",
                content=content,
                timestamp=self._current_timestamp(),
            ),
        )

    def add_assistant_message(
        self,
        session_id: str,
        content: str,
        intent: IntentType,
    ) -> None:
        """Store an assistant response in a conversation session."""
        self._add_message(
            session_id=session_id,
            message=ConversationMessage(
                role="assistant",
                content=content,
                timestamp=self._current_timestamp(),
                intent=intent,
            ),
        )

    def get_history(self, session_id: str) -> list[ConversationMessage]:
        """Return stored messages for a conversation session."""
        normalized_session_id = self._normalize_session_id(session_id)
        if normalized_session_id is None:
            raise ValueError("session_id cannot be empty.")

        with self._lock:
            session = self._sessions.get(normalized_session_id)
            if session is None:
                return []

            return list(session.messages)

    def _add_message(
        self,
        session_id: str,
        message: ConversationMessage,
    ) -> None:
        """Append a message to an existing or new session."""
        normalized_session_id = self.get_or_create_session(session_id)

        with self._lock:
            self._sessions[normalized_session_id].messages.append(message)

    @staticmethod
    def _normalize_session_id(session_id: str | None) -> str | None:
        """Normalize optional session IDs and reject blank values."""
        if session_id is None:
            return None

        normalized_session_id = session_id.strip()
        if not normalized_session_id:
            raise ValueError("session_id cannot be empty.")

        return normalized_session_id

    @staticmethod
    def _current_timestamp() -> str:
        """Return the current UTC timestamp as an ISO 8601 string."""
        return datetime.now(UTC).isoformat()


conversation_memory = ConversationMemory()
