"""Utility modules for llm_midi package."""

from .logging import (
    setup_logging,
    setup_app_logging,
    get_logger,
    debug_logging,
    quiet_logging,
    ColoredFormatter,
    LoggingContext
)
from .music_theory import (
    note_to_midi,
    midi_to_note,
    parse_note,
    parse_chord,
    get_chord_notes,
    get_scale_notes,
    validate_chord_progression,
    validate_melody_patterns,
    transpose_chord,
    get_chord_name_from_notes,
    CHORD_PATTERNS,
    SCALE_PATTERNS,
    MIDI_TO_NOTE,
    NOTE_TO_MIDI
)
from .parser import (
    ResponseParser,
    parse_response,
    ParseError
)

__all__ = [
    # Logging utilities
    "setup_logging",
    "setup_app_logging",
    "get_logger",
    "debug_logging",
    "quiet_logging",
    "ColoredFormatter",
    "LoggingContext",

    # Music theory utilities
    "note_to_midi",
    "midi_to_note",
    "parse_note",
    "parse_chord",
    "get_chord_notes",
    "get_scale_notes",
    "validate_chord_progression",
    "validate_melody_patterns",
    "transpose_chord",
    "get_chord_name_from_notes",
    "CHORD_PATTERNS",
    "SCALE_PATTERNS",
    "MIDI_TO_NOTE",
    "NOTE_TO_MIDI",

    # Parser utilities
    "ResponseParser",
    "parse_response",
    "ParseError",
]
