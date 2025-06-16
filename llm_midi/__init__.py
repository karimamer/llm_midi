"""
llm_midi - AI-powered MIDI generation using Large Language Models.

This package provides tools for generating musical compositions by leveraging
AI to create chord progressions and melody patterns, then converting them
into MIDI files.
"""

__version__ = "0.1.0"

# Core functionality
from .core import (
    AppConfig,
    MusicConfig,
    AIConfig,
    get_config,
    LLMClient,
    MidiGenerator,
    generate_song_name,
    create_midi_file
)

# Main entry points
from .main import main
from .cli import main as cli_main

# Utilities (selected exports)
from .utils import (
    get_logger,
    setup_app_logging,
    parse_response,
    ParseError,
    note_to_midi,
    midi_to_note,
    get_chord_notes,
    validate_chord_progression,
    validate_melody_patterns
)

__all__ = [
    # Version
    "__version__",

    # Configuration
    "AppConfig",
    "MusicConfig",
    "AIConfig",
    "get_config",

    # Core functionality
    "LLMClient",
    "MidiGenerator",
    "generate_song_name",
    "create_midi_file",

    # Main entry points
    "main",
    "cli_main",

    # Key utilities
    "get_logger",
    "setup_app_logging",
    "parse_response",
    "ParseError",
    "note_to_midi",
    "midi_to_note",
    "get_chord_notes",
    "validate_chord_progression",
    "validate_melody_patterns",
]
