"""Pipecat Voice Bot for the Focus Agent.

Runs a WebRTC-based voice interface that lets users speak tasks
and hear the Focus Agent's task breakdown response.

Usage:
    uv run voice_bot.py

Then open http://localhost:7860/client in your browser.

Required env vars:
    DEEPGRAM_API_KEY  - For both STT and TTS
    GROQ_API_KEY      - For the LangGraph Focus Agent's LLM
"""

import os

from dotenv import load_dotenv
from loguru import logger

print("🚀 Starting Focus Agent Voice Bot...")
print("⏳ Loading models and imports (may take ~20s on first run)\n")

logger.info("Loading Silero VAD model...")
from pipecat.audio.vad.silero import SileroVADAnalyzer

logger.info("✅ Silero VAD model loaded")

from pipecat.frames.frames import LLMRunFrame
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.aggregators.llm_response_universal import (
    LLMContextAggregatorPair,
    LLMUserAggregatorParams,
)
from pipecat.runner.types import RunnerArguments
from pipecat.runner.utils import create_transport
from pipecat.services.deepgram.stt import DeepgramSTTService
from pipecat.services.deepgram.tts import DeepgramTTSService
from pipecat.transports.base_transport import BaseTransport, TransportParams

from src.voice_processor import FocusAgentProcessor

logger.info("✅ All components loaded successfully!")

load_dotenv(override=True)


async def run_bot(transport: BaseTransport, runner_args: RunnerArguments):
    logger.info("Starting Focus Agent Voice Bot")

    stt = DeepgramSTTService(api_key=os.getenv("DEEPGRAM_API_KEY"))

    tts = DeepgramTTSService(
        api_key=os.getenv("DEEPGRAM_API_KEY"),
        voice="aura-asteria-en",
    )

    # Custom processor that invokes the LangGraph Focus Agent
    focus_agent = FocusAgentProcessor()

    # System message sets the conversational context
    messages = [
        {
            "role": "system",
            "content": (
                "You are a voice-enabled Focus Agent that helps break down tasks "
                "into actionable steps. Listen to the user's task description and "
                "provide a clear, structured breakdown."
            ),
        },
    ]

    context = LLMContext(messages)
    user_aggregator, assistant_aggregator = LLMContextAggregatorPair(
        context,
        user_params=LLMUserAggregatorParams(
            vad_analyzer=SileroVADAnalyzer(),
        ),
    )

    pipeline = Pipeline(
        [
            transport.input(),        # Receive audio from browser
            stt,                      # Speech-to-text (Deepgram)
            user_aggregator,          # Aggregate user speech into context
            focus_agent,              # LangGraph Focus Agent (replaces LLM)
            tts,                      # Text-to-speech (Deepgram)
            transport.output(),       # Send audio back to browser
            assistant_aggregator,     # Track assistant responses in context
        ]
    )

    task = PipelineTask(
        pipeline,
        params=PipelineParams(
            enable_metrics=True,
            enable_usage_metrics=True,
        ),
    )

    @transport.event_handler("on_client_connected")
    async def on_client_connected(transport, client):
        logger.info("Client connected")
        messages.append(
            {
                "role": "system",
                "content": "Greet the user and tell them you are the Focus Agent, "
                "ready to help break down any task into actionable steps. "
                "Ask them what task they'd like to break down.",
            }
        )
        await task.queue_frames([LLMRunFrame()])

    @transport.event_handler("on_client_disconnected")
    async def on_client_disconnected(transport, client):
        logger.info("Client disconnected")
        await task.cancel()

    runner = PipelineRunner(handle_sigint=runner_args.handle_sigint)
    await runner.run(task)


async def bot(runner_args: RunnerArguments):
    """Main bot entry point."""
    transport_params = {
        "webrtc": lambda: TransportParams(
            audio_in_enabled=True,
            audio_out_enabled=True,
        ),
    }

    transport = await create_transport(runner_args, transport_params)
    await run_bot(transport, runner_args)


if __name__ == "__main__":
    from pipecat.runner.run import main

    main()
