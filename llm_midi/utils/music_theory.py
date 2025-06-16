"""Music theory utilities for MIDI generation."""

import re
from typing import Dict, List, Optional, Tuple, Union

# MIDI note number to note name mapping
MIDI_TO_NOTE: Dict[int, str] = {
    0: "C", 1: "C#", 2: "D", 3: "D#", 4: "E", 5: "F",
    6: "F#", 7: "G", 8: "G#", 9: "A", 10: "A#", 11: "B"
}

# Note name to MIDI note number mapping (within octave 0)
NOTE_TO_MIDI: Dict[str, int] = {v: k for k, v in MIDI_TO_NOTE.items()}

# Alternative note names (flats)
NOTE_ALIASES: Dict[str, str] = {
    "Db": "C#", "Eb": "D#", "Gb": "F#", "Ab": "G#", "Bb": "A#"
}

# Common chord types with their interval patterns (semitones from root)
CHORD_PATTERNS: Dict[str, List[int]] = {
    "": [0, 4, 7],          # Major triad
    "maj": [0, 4, 7],       # Major triad
    "M": [0, 4, 7],         # Major triad
    "m": [0, 3, 7],         # Minor triad
    "min": [0, 3, 7],       # Minor triad
    "dim": [0, 3, 6],       # Diminished triad
    "aug": [0, 4, 8],       # Augmented triad
    "sus2": [0, 2, 7],      # Suspended 2nd
    "sus4": [0, 5, 7],      # Suspended 4th
    "7": [0, 4, 7, 10],     # Dominant 7th
    "maj7": [0, 4, 7, 11],  # Major 7th
    "m7": [0, 3, 7, 10],    # Minor 7th
    "dim7": [0, 3, 6, 9],   # Diminished 7th
    "add9": [0, 4, 7, 14],  # Add 9th
}

# Common scales with their interval patterns
SCALE_PATTERNS: Dict[str, List[int]] = {
    "major": [0, 2, 4, 5, 7, 9, 11],
    "minor": [0, 2, 3, 5, 7, 8, 10],
    "harmonic_minor": [0, 2, 3, 5, 7, 8, 11],
    "melodic_minor": [0, 2, 3, 5, 7, 9, 11],
    "dorian": [0, 2, 3, 5, 7, 9, 10],
    "phrygian": [0, 1, 3, 5, 7, 8, 10],
    "lydian": [0, 2, 4, 6, 7, 9, 11],
    "mixolydian": [0, 2, 4, 5, 7, 9, 10],
    "pentatonic": [0, 2, 4, 7, 9],
    "blues": [0, 3, 5, 6, 7, 10],
}

# MIDI note ranges
MIDI_MIN = 0
MIDI_MAX = 127
MIDDLE_C = 60  # C4


def parse_note(note_str: str) -> Tuple[str, int]:
    """
    Parse a note string into note name and octave.

    Args:
        note_str: Note string like "C4", "F#3", "Bb5"

    Returns:
        Tuple of (note_name, octave)

    Raises:
        ValueError: If note string is invalid
    """
    pattern = r"^([A-G][#b]?)(\d+)$"
    match = re.match(pattern, note_str)

    if not match:
        raise ValueError(f"Invalid note format: {note_str}")

    note_name, octave_str = match.groups()
    octave = int(octave_str)

    # Normalize note name (convert flats to sharps)
    if note_name in NOTE_ALIASES:
        note_name = NOTE_ALIASES[note_name]

    if note_name not in NOTE_TO_MIDI:
        raise ValueError(f"Invalid note name: {note_name}")

    return note_name, octave


def note_to_midi(note_str: str) -> int:
    """
    Convert a note string to MIDI note number.

    Args:
        note_str: Note string like "C4", "F#3", "Bb5"

    Returns:
        MIDI note number (0-127)

    Raises:
        ValueError: If note string is invalid or results in out-of-range MIDI number
    """
    note_name, octave = parse_note(note_str)

    # Calculate MIDI number: (octave + 1) * 12 + note offset
    # This follows the standard where C4 (middle C) = 60
    midi_number = (octave + 1) * 12 + NOTE_TO_MIDI[note_name]

    if not (MIDI_MIN <= midi_number <= MIDI_MAX):
        raise ValueError(f"MIDI note number {midi_number} out of range ({MIDI_MIN}-{MIDI_MAX})")

    return midi_number


def midi_to_note(midi_number: int, prefer_sharps: bool = True) -> str:
    """
    Convert MIDI note number to note string.

    Args:
        midi_number: MIDI note number (0-127)
        prefer_sharps: If True, use sharps instead of flats for black keys

    Returns:
        Note string like "C4", "F#3", "Bb5"

    Raises:
        ValueError: If MIDI number is out of range
    """
    if not (MIDI_MIN <= midi_number <= MIDI_MAX):
        raise ValueError(f"MIDI note number {midi_number} out of range ({MIDI_MIN}-{MIDI_MAX})")

    octave = (midi_number // 12) - 1
    note_offset = midi_number % 12
    note_name = MIDI_TO_NOTE[note_offset]

    # Convert to flat if requested and it's a black key
    if not prefer_sharps and "#" in note_name:
        flat_equivalents = {v: k for k, v in NOTE_ALIASES.items()}
        if note_name in flat_equivalents:
            note_name = flat_equivalents[note_name]

    return f"{note_name}{octave}"


def parse_chord(chord_str: str) -> Tuple[str, str]:
    """
    Parse a chord string into root note and chord type.

    Args:
        chord_str: Chord string like "Cm", "F#maj7", "Bb"

    Returns:
        Tuple of (root_note, chord_type)

    Raises:
        ValueError: If chord string is invalid
    """
    # Pattern to match root note and chord type
    pattern = r"^([A-G][#b]?)(.*?)$"
    match = re.match(pattern, chord_str)

    if not match:
        raise ValueError(f"Invalid chord format: {chord_str}")

    root_note, chord_type = match.groups()

    # Normalize root note
    if root_note in NOTE_ALIASES:
        root_note = NOTE_ALIASES[root_note]

    if root_note not in NOTE_TO_MIDI:
        raise ValueError(f"Invalid root note: {root_note}")

    return root_note, chord_type


def get_chord_notes(chord_str: str, octave: int = 4) -> List[int]:
    """
    Get MIDI note numbers for a chord.

    Args:
        chord_str: Chord string like "Cm", "F#maj7", "Bb"
        octave: Base octave for the chord

    Returns:
        List of MIDI note numbers

    Raises:
        ValueError: If chord is invalid or unknown
    """
    root_note, chord_type = parse_chord(chord_str)

    if chord_type not in CHORD_PATTERNS:
        raise ValueError(f"Unknown chord type: {chord_type}")

    root_midi = note_to_midi(f"{root_note}{octave}")
    pattern = CHORD_PATTERNS[chord_type]

    return [root_midi + interval for interval in pattern]


def get_scale_notes(root: str, scale_type: str, octave: int = 4) -> List[int]:
    """
    Get MIDI note numbers for a scale.

    Args:
        root: Root note name like "C", "F#", "Bb"
        scale_type: Scale type like "major", "minor", "pentatonic"
        octave: Base octave for the scale

    Returns:
        List of MIDI note numbers

    Raises:
        ValueError: If root note or scale type is invalid
    """
    # Normalize root note
    if root in NOTE_ALIASES:
        root = NOTE_ALIASES[root]

    if root not in NOTE_TO_MIDI:
        raise ValueError(f"Invalid root note: {root}")

    if scale_type not in SCALE_PATTERNS:
        raise ValueError(f"Unknown scale type: {scale_type}")

    root_midi = note_to_midi(f"{root}{octave}")
    pattern = SCALE_PATTERNS[scale_type]

    return [root_midi + interval for interval in pattern]


def validate_chord_progression(chords: List[Tuple[str, List[int]]]) -> bool:
    """
    Validate a chord progression structure.

    Args:
        chords: List of (chord_name, midi_notes) tuples

    Returns:
        True if valid, False otherwise
    """
    if not chords:
        return False

    for chord_name, midi_notes in chords:
        # Check chord name is string
        if not isinstance(chord_name, str):
            return False

        # Check MIDI notes is list of integers
        if not isinstance(midi_notes, list):
            return False

        if not all(isinstance(note, int) for note in midi_notes):
            return False

        # Check MIDI notes are in valid range
        if not all(MIDI_MIN <= note <= MIDI_MAX for note in midi_notes):
            return False

        # Check we have at least 2 notes (for intervals)
        if len(midi_notes) < 2:
            return False

    return True


def validate_melody_patterns(patterns: List[List[int]]) -> bool:
    """
    Validate melody patterns structure.

    Args:
        patterns: List of melody patterns (lists of interval integers)

    Returns:
        True if valid, False otherwise
    """
    if not patterns:
        return False

    for pattern in patterns:
        # Check pattern is list of integers
        if not isinstance(pattern, list):
            return False

        if not all(isinstance(interval, int) for interval in pattern):
            return False

        # Check pattern has reasonable length
        if len(pattern) < 2:
            return False

        # Check intervals are reasonable (within 2 octaves)
        if not all(-24 <= interval <= 24 for interval in pattern):
            return False

    return True


def transpose_chord(chord_notes: List[int], semitones: int) -> List[int]:
    """
    Transpose a chord by a number of semitones.

    Args:
        chord_notes: List of MIDI note numbers
        semitones: Number of semitones to transpose (positive = up, negative = down)

    Returns:
        List of transposed MIDI note numbers

    Raises:
        ValueError: If transposition results in out-of-range notes
    """
    transposed = [note + semitones for note in chord_notes]

    if not all(MIDI_MIN <= note <= MIDI_MAX for note in transposed):
        raise ValueError("Transposition results in out-of-range MIDI notes")

    return transposed


def get_chord_name_from_notes(midi_notes: List[int]) -> Optional[str]:
    """
    Attempt to identify a chord name from MIDI notes.

    Args:
        midi_notes: List of MIDI note numbers

    Returns:
        Chord name string or None if not recognized
    """
    if len(midi_notes) < 2:
        return None

    # Sort notes and get intervals from the lowest note
    sorted_notes = sorted(midi_notes)
    root = sorted_notes[0]
    intervals = [note - root for note in sorted_notes]

    # Normalize intervals to within one octave
    normalized_intervals = [interval % 12 for interval in intervals]
    normalized_intervals = sorted(list(set(normalized_intervals)))  # Remove duplicates and sort

    # Try to match against known chord patterns
    for chord_type, pattern in CHORD_PATTERNS.items():
        if normalized_intervals == sorted(pattern[:len(normalized_intervals)]):
            root_note = midi_to_note(root % 12)  # Get note name without octave
            chord_suffix = chord_type if chord_type else ""
            return f"{root_note}{chord_suffix}"

    return None
