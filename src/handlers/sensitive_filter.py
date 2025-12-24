import json
import time

from fastapi.responses import StreamingResponse

from log import logger
from schemas.base import Success
from utils.sensitive_word_filter import sensitive_word_filter


class SensitiveFilterHandler:
    """Unified sensitive word handler"""

    def __init__(self):
        self.filter = sensitive_word_filter

    def check_input(self, text: str) -> tuple[bool, str | None]:
        """Check if input text contains sensitive words

        Returns:
            Tuple[bool, Optional[str]]: (whether contains sensitive words, matched sensitive word)
        """
        return self.filter.contains_sensitive_word(text)

    async def handle_sensitive_input_stream(self, matched_word: str, query: str):
        """Handle streaming request containing sensitive words"""
        logger.warning(f"User input contains sensitive word '{matched_word}': {query[:100]}")

        async def sensitive_word_response():
            # Send sensitive word reminder
            error_event = {
                "event": "error",
                "answer": self.filter.response_message,
            }
            yield f"data: {json.dumps(error_event, ensure_ascii=False)}\n\n"
            # Send end signal
            yield "data: [DONE]\n\n"

        return StreamingResponse(
            sensitive_word_response(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
            },
        )

    def handle_sensitive_input_sync(self, matched_word: str, query: str):
        """Handle synchronous request containing sensitive words"""
        logger.warning(f"User input contains sensitive word '{matched_word}': {query[:100]}")
        return Success(
            data={
                "status": "blocked",
                "message": self.filter.response_message,
                "code": "SENSITIVE_CONTENT_DETECTED",
            }
        )

    def filter_chunk(self, chunk: str) -> str | None:
        """Filter sensitive words from data chunk"""
        return self.filter.filter_streaming_chunk(chunk)

    def create_sensitive_response_data(self, event_data: dict | None = None) -> dict:
        """Create sensitive word response data"""
        return {
            "event": "workflow_finished",
            "data": {"outputs": {"answer": self.filter.response_message}},
            "message_id": event_data.get("message_id") if event_data else "",
            "workflow_run_id": (
                event_data.get("workflow_run_id") if event_data else ""
            ),
            "created_at": int(time.time()),
        }

    def create_sensitive_stream_message(self, event_data: dict | None = None) -> dict:
        """Create sensitive word streaming message"""
        return {
            "event": "error",
            "message_id": event_data.get("message_id") if event_data else "",
            "conversation_id": (
                event_data.get("conversation_id") if event_data else ""
            ),
            "answer": self.filter.response_message,
        }


# Global instance
sensitive_filter_handler = SensitiveFilterHandler()
