"""Modular, event-driven audio-to-text pipeline."""

from .config import AudioSTTConfig
from .events import AudioEvent, EventKind, Transcript
from .pipeline import AudioToTextPipeline

__all__ = [
    "AudioEvent",
    "AudioSTTConfig",
    "AudioToTextPipeline",
    "EventKind",
    "Transcript",
]
