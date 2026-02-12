"""Custom Pipecat FrameProcessor that wraps the LangGraph Focus Agent.

Sits in the pipeline where an LLM service would normally go.
Receives LLMMessagesFrame from the context aggregator, invokes the
LangGraph graph, and pushes TextFrames downstream to TTS.
"""

import uuid

from loguru import logger

from pipecat.frames.frames import (
    Frame,
    LLMFullResponseEndFrame,
    LLMFullResponseStartFrame,
    LLMMessagesFrame,
    TextFrame,
)
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor

from langchain_core.messages import HumanMessage
from src.graph import graph


class FocusAgentProcessor(FrameProcessor):
    """Pipecat processor that delegates to the LangGraph Focus Agent."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._thread_id = str(uuid.uuid4())
        logger.info(f"FocusAgentProcessor initialized (thread={self._thread_id})")

    async def process_frame(self, frame: Frame, direction: FrameDirection):
        await super().process_frame(frame, direction)

        if isinstance(frame, LLMMessagesFrame):
            await self._handle_llm_messages(frame)
        else:
            await self.push_frame(frame, direction)

    async def _handle_llm_messages(self, frame: LLMMessagesFrame):
        """Extract the latest user message, invoke the LangGraph agent,
        and push the response as TextFrames for TTS."""

        # Extract the last user message from the OpenAI-format messages
        user_text = None
        for msg in reversed(frame.messages):
            if isinstance(msg, dict) and msg.get("role") == "user":
                content = msg.get("content", "")
                if isinstance(content, str) and content.strip():
                    user_text = content.strip()
                    break
                elif isinstance(content, list):
                    # Handle list-format content (multimodal)
                    for part in content:
                        if isinstance(part, dict) and part.get("type") == "text":
                            user_text = part.get("text", "").strip()
                            break
                    if user_text:
                        break

        if not user_text:
            logger.warning("No user text found in LLMMessagesFrame, skipping")
            return

        logger.info(f"Invoking Focus Agent with: {user_text!r}")

        try:
            result = graph.invoke(
                {"messages": [HumanMessage(content=user_text)]},
                config={"configurable": {"thread_id": self._thread_id}},
            )

            response_text = result["messages"][-1].content
            logger.info(f"Focus Agent response length: {len(response_text)} chars")

            # Push LLM response frames downstream so TTS and context
            # aggregator handle them correctly
            await self.push_frame(LLMFullResponseStartFrame())
            await self.push_frame(TextFrame(text=response_text))
            await self.push_frame(LLMFullResponseEndFrame())

        except Exception as e:
            logger.error(f"Focus Agent invocation failed: {e}")
            await self.push_frame(LLMFullResponseStartFrame())
            await self.push_frame(
                TextFrame(text="Sorry, I encountered an error processing your request.")
            )
            await self.push_frame(LLMFullResponseEndFrame())
