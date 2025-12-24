import json

from log import logger


class DataProcessor:
    """Data processing utility class - consolidates all duplicate data processing logic"""

    @staticmethod
    def extract_workflow_data(chunks: list[str]) -> dict | None:
        """Extract workflow_finished event data from data chunks - unified version"""
        logger.info(f"Starting to extract workflow_finished event from {len(chunks)} data chunks")

        found_event_types = []

        # Search from back to front, latest events are at the end
        for i, chunk in enumerate(reversed(chunks)):
            if chunk.startswith("data:"):
                json_content_str = chunk[len("data:") :].strip()
                if json_content_str and json_content_str != "[DONE]":
                    try:
                        event_data = json.loads(json_content_str)
                        event_type = event_data.get("event")
                        if event_type:
                            found_event_types.append(event_type)

                        if event_type == "workflow_finished":
                            logger.info(
                                f"Found workflow_finished event in chunk {len(chunks) - 1 - i}"
                            )
                            return event_data
                    except json.JSONDecodeError as e:
                        logger.warning(
                            f"Failed to parse data chunk: {str(e)}, content: {json_content_str[:100]}..."
                        )
                        continue

        logger.warning(
            f"workflow_finished event not found. Traversed {len(chunks)} data chunks, "
            f"found event types: {found_event_types}"
        )
        return None

    @staticmethod
    def extract_text_from_chunks(chunks: list[str]) -> str:
        """Extract accumulated text content from data chunks"""
        accumulated_text = ""

        for chunk in chunks:
            if chunk.startswith("data:"):
                json_content_str = chunk[len("data:") :].strip()
                if json_content_str and json_content_str != "[DONE]":
                    try:
                        event_data = json.loads(json_content_str)
                        event_type = event_data.get("event")

                        # Extract text from different event types
                        if event_type == "text_chunk":
                            text = event_data.get("data", {}).get("text", "")
                            if text:
                                accumulated_text += text
                        elif event_type == "agent_message":
                            text = event_data.get("data", {}).get("answer", "")
                            if text:
                                accumulated_text += text
                        elif event_type == "message":
                            # Check if there is output content
                            data = event_data.get("data", {})
                            if data.get("outputs"):
                                answer = data.get("outputs", {}).get("answer", "")
                                if answer:
                                    accumulated_text = answer  # Use final answer
                            elif data.get("answer"):
                                accumulated_text = data.get("answer")
                    except json.JSONDecodeError:
                        continue

        return accumulated_text.strip()

    @staticmethod
    def parse_chunk_event(chunk: str) -> dict | None:
        """Parse event from data chunk"""
        if not chunk.startswith("data:"):
            return None

        json_content_str = chunk[len("data:") :].strip()
        if not json_content_str or json_content_str == "[DONE]":
            return None

        try:
            return json.loads(json_content_str)
        except json.JSONDecodeError:
            return None

    @staticmethod
    def generate_title(query: str, answer: str) -> str:
        """Generate title"""
        if query and answer:
            return f"{query} - {answer}"[:50]
        elif query:
            return query[:50]
        elif answer:
            return answer[:50]
        else:
            return "New Chat"


# Global instance
data_processor = DataProcessor()
