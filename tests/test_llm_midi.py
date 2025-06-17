import pytest
from unittest.mock import Mock, patch

from llm_midi import __version__
from llm_midi.core.config import MusicConfig, AIConfig, AppConfig
from llm_midi.core.midi_generator import SongNameGenerator, MidiGenerator
from llm_midi.utils.music_theory import (
    note_to_midi, midi_to_note, parse_chord, get_chord_notes,
    validate_chord_progression, validate_melody_patterns
)
from llm_midi.utils.parser import ResponseParser


def test_version():
    assert __version__ == "0.1.0"


def test_music_config_defaults():
    """Test that MusicConfig has reasonable defaults."""
    config = MusicConfig()
    assert config.tempo_bpm == 120
    assert config.ticks_per_beat == 480
    assert config.min_chords >= 1
    assert config.max_chords >= config.min_chords


def test_ai_config_with_mock_key():
    """Test AIConfig with a mock API key."""
    with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'}):
        config = AIConfig()
        assert config.api_key == 'test-key'
        assert config.model == "claude-3-opus-20240229"


def test_app_config():
    """Test that AppConfig initializes sub-configs properly."""
    with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'}):
        config = AppConfig()
        assert isinstance(config.music, MusicConfig)
        assert isinstance(config.ai, AIConfig)


def test_song_name_generator():
    """Test that song name generator produces valid strings."""
    generator = SongNameGenerator()
    name = generator.generate()
    assert isinstance(name, str)
    assert len(name) > 0


def test_note_to_midi():
    """Test note to MIDI conversion."""
    assert note_to_midi("C4") == 60  # Middle C
    assert note_to_midi("A4") == 69  # Concert A
    assert note_to_midi("C#3") == 49


def test_midi_to_note():
    """Test MIDI to note conversion."""
    assert midi_to_note(60) == "C4"  # Middle C
    assert midi_to_note(69) == "A4"  # Concert A


def test_parse_chord():
    """Test chord parsing."""
    root, chord_type = parse_chord("Cm")
    assert root == "C"
    assert chord_type == "m"

    root, chord_type = parse_chord("F#maj7")
    assert root == "F#"
    assert chord_type == "maj7"


def test_get_chord_notes():
    """Test chord note generation."""
    # C major triad
    notes = get_chord_notes("C", octave=4)
    assert len(notes) == 3
    assert 60 in notes  # C4

    # C minor triad
    notes = get_chord_notes("Cm", octave=4)
    assert len(notes) == 3


def test_validate_chord_progression():
    """Test chord progression validation."""
    # Valid progression
    chords = [
        ("C", [60, 64, 67]),
        ("F", [65, 69, 72]),
        ("G", [67, 71, 74])
    ]
    assert validate_chord_progression(chords)

    # Invalid progression (empty)
    assert not validate_chord_progression([])

    # Invalid progression (not enough notes)
    invalid_chords = [("C", [60])]
    assert not validate_chord_progression(invalid_chords)


def test_validate_melody_patterns():
    """Test melody pattern validation."""
    # Valid patterns
    patterns = [
        [0, 2, 4, 2, 0],
        [-2, 0, 2, 4, 2]
    ]
    assert validate_melody_patterns(patterns)

    # Invalid patterns (empty)
    assert not validate_melody_patterns([])

    # Invalid patterns (too short)
    invalid_patterns = [[0]]
    assert not validate_melody_patterns(invalid_patterns)


def test_response_parser_extract_text():
    """Test text extraction from various response formats."""
    # Simple string
    text = ResponseParser.extract_text_content("test content")
    assert text == "test content"

    # Mock TextBlock format
    mock_response = [Mock()]
    mock_response[0].text = "mock text content"
    text = ResponseParser.extract_text_content(mock_response)
    assert text == "mock text content"


def test_response_parser_python_code():
    """Test parsing of Python code responses."""
    sample_response = '''
chords = [
    ("C", [60, 64, 67]),
    ("F", [65, 69, 72])
]
melody_patterns = [
    [0, 2, 4, 2, 0],
    [-2, 0, 2, 0]
]
'''

    chords, patterns = ResponseParser.parse_python_code(sample_response)
    assert len(chords) == 2
    assert len(patterns) == 2
    assert chords[0][0] == "C"
    assert chords[0][1] == [60, 64, 67]


def test_midi_generator_requires_config():
    """Test that MidiGenerator requires a config."""
    config = MusicConfig()
    generator = MidiGenerator(config)
    assert generator.config == config


def test_midi_generator_with_valid_data():
    """Test MIDI generation with valid chord and pattern data."""
    config = MusicConfig()
    generator = MidiGenerator(config)

    chords = [("C", [60, 64, 67])]
    patterns = [[0, 2, 4, 2, 0]]

    midi_file = generator.create_midi_file(chords, patterns)
    assert midi_file is not None
    assert len(midi_file.tracks) > 0


def test_midi_generator_invalid_input():
    """Test MIDI generator with invalid input."""
    config = MusicConfig()
    generator = MidiGenerator(config)

    # No chords
    with pytest.raises(ValueError):
        generator.create_midi_file([], [[0, 2, 4]])

    # No patterns
    with pytest.raises(ValueError):
        generator.create_midi_file([("C", [60, 64, 67])], [])
