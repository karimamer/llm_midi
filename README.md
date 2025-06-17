# LLM MIDI

AI-powered MIDI generation using Large Language Models. This tool leverages Claude AI to generate musically coherent chord progressions and melody patterns, then converts them into MIDI files for use in your music production workflow.

## Features

- 🎵 **AI-Generated Music**: Uses Claude AI to create chord progressions and melody patterns
- 🎹 **MIDI Output**: Generates standard MIDI files compatible with any DAW
- 🎛️ **Configurable Parameters**: Customize tempo, number of chords, melody patterns, and more
- 🧩 **Modular Architecture**: Clean, extensible codebase with separate concerns
- 🎨 **Creative Song Names**: Auto-generates creative song titles
- 📝 **Rich CLI Interface**: Full-featured command-line interface with extensive options
- 🔧 **Programmatic API**: Use as a Python library in your own projects
- ✅ **Music Theory Validation**: Built-in validation for musical coherence

## Installation

### Prerequisites

- Python 3.10 or higher
- An Anthropic API key (get one at [https://console.anthropic.com/](https://console.anthropic.com/))

### Install from source

```bash
git clone <repository-url>
cd llm_midi
poetry install
```

### Set up your API key

```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

Or create a `.env` file in the project root:
```
ANTHROPIC_API_KEY=your-api-key-here
```

## Quick Start

### Command Line Usage

Generate a MIDI file with default settings:
```bash
llm-midi
```

Generate with custom parameters:
```bash
llm-midi --tempo 140 --chords 8 --patterns 5 -o my_song.mid
```

See all available options:
```bash
llm-midi --help
```

### Programmatic Usage

```python
from llm_midi import main, MusicConfig, AIConfig, AppConfig

# Simple usage
main(output_path="my_song.mid")

# Advanced usage with custom configuration
music_config = MusicConfig(tempo_bpm=140, bars_per_chord=4)
ai_config = AIConfig(temperature=0.8)
config = AppConfig(music=music_config, ai=ai_config)

from llm_midi import LLMClient, MidiGenerator, ResponseParser

client = LLMClient(config.ai)
response = client.generate_musical_content()
chords, patterns = ResponseParser.parse_response(response)
generator = MidiGenerator(config.music)
midi_file = generator.create_midi_file(chords, patterns)
midi_file.save("custom_song.mid")
```

## Architecture

The project is organized into a clean, modular structure:

```
llm_midi/
├── core/                    # Core business logic
│   ├── config.py           # Configuration management
│   ├── llm_client.py       # Claude AI integration
│   └── midi_generator.py   # MIDI file generation
├── utils/                   # Utility modules
│   ├── logging.py          # Logging utilities
│   ├── music_theory.py     # Music theory helpers
│   └── parser.py           # Response parsing
├── cli.py                  # Command-line interface
└── main.py                 # Main entry point
```

### Core Modules

#### Configuration (`core/config.py`)
- `MusicConfig`: Musical parameters (tempo, chords, patterns, etc.)
- `AIConfig`: AI model settings (temperature, tokens, etc.)
- `AppConfig`: Combined application configuration

#### LLM Client (`core/llm_client.py`)
- `LLMClient`: Interface to Claude AI for generating musical content
- Handles API communication and error management

#### MIDI Generator (`core/midi_generator.py`)
- `MidiGenerator`: Converts chord progressions and patterns to MIDI
- `SongNameGenerator`: Creates creative song titles

### Utility Modules

#### Music Theory (`utils/music_theory.py`)
- Note/MIDI conversion functions
- Chord and scale utilities
- Music theory validation

#### Parser (`utils/parser.py`)
- `ResponseParser`: Parses Claude AI responses
- Robust parsing with fallback methods
- Data validation

#### Logging (`utils/logging.py`)
- Colored console output
- File logging support
- Debug mode capabilities

## Configuration Options

### Music Configuration

```python
MusicConfig(
    tempo_bpm=120,           # Tempo in beats per minute
    ticks_per_beat=480,      # MIDI ticks per beat
    beats_per_bar=4,         # Time signature
    chord_velocity=64,       # MIDI velocity for chords
    melody_velocity=80,      # MIDI velocity for melody
    bars_per_chord=2,        # Bars each chord is played
    min_chords=5,            # Minimum number of chords
    max_chords=10,           # Maximum number of chords
    min_melody_patterns=3,   # Minimum melody patterns
    max_melody_patterns=6,   # Maximum melody patterns
    min_pattern_length=4,    # Minimum pattern length
    max_pattern_length=12    # Maximum pattern length
)
```

### AI Configuration

```python
AIConfig(
    model="claude-3-opus-20240229",  # Claude model to use
    max_tokens=1000,                 # Maximum response tokens
    temperature=0.7,                 # Creativity level (0.0-1.0)
    api_key=None                     # API key (auto-loaded from env)
)
```

## CLI Reference

```
llm-midi [options]

Output Options:
  -o, --output FILENAME        Output MIDI filename
  --output-dir DIR            Output directory

Music Generation Options:
  --chords N                  Number of chords to generate
  --patterns N                Number of melody patterns
  --tempo BPM                 Tempo in beats per minute
  --bars-per-chord N          Number of bars per chord

AI Options:
  --model MODEL               Claude model to use
  --temperature T             AI creativity (0.0-1.0)
  --max-tokens N              Maximum AI response tokens

Logging Options:
  --debug                     Enable debug logging
  --quiet                     Suppress output except errors
  --log-dir DIR               Directory for log files

Utility Options:
  --dry-run                   Generate content but don't create MIDI
  --version                   Show version information
```

## API Reference

### Core Classes

#### `LLMClient(config: AIConfig)`
- `generate_musical_content(**kwargs) -> str`: Generate musical content from Claude

#### `MidiGenerator(config: MusicConfig)`
- `create_midi_file(chords, patterns) -> MidiFile`: Create MIDI from musical data

#### `ResponseParser`
- `parse_response(response) -> Tuple[chords, patterns]`: Parse Claude response

### Utility Functions

#### Music Theory
- `note_to_midi(note_str: str) -> int`: Convert note to MIDI number
- `midi_to_note(midi_num: int) -> str`: Convert MIDI number to note
- `get_chord_notes(chord_str: str, octave: int) -> List[int]`: Get MIDI notes for chord

#### Validation
- `validate_chord_progression(chords) -> bool`: Validate chord structure
- `validate_melody_patterns(patterns) -> bool`: Validate pattern structure

## Examples

### Custom Chord Progressions

```python
from llm_midi.utils.music_theory import get_chord_notes
from llm_midi import create_midi_file

# Create custom chord progression
chords = [
    ("C", get_chord_notes("C", 4)),
    ("Am", get_chord_notes("Am", 4)),
    ("F", get_chord_notes("F", 4)),
    ("G", get_chord_notes("G", 4))
]

# Create melody patterns
patterns = [
    [0, 2, 4, 2, 0, -2, 0],
    [4, 2, 0, 2, 4, 6, 4]
]

# Generate MIDI
midi_file = create_midi_file(chords, patterns)
midi_file.save("custom_progression.mid")
```

### Batch Generation

```python
from llm_midi import LLMClient, MidiGenerator, ResponseParser
from llm_midi.core.config import get_config

config = get_config()
client = LLMClient(config.ai)
generator = MidiGenerator(config.music)

# Generate multiple songs
for i in range(5):
    response = client.generate_musical_content()
    chords, patterns = ResponseParser.parse_response(response)
    midi_file = generator.create_midi_file(chords, patterns)
    midi_file.save(f"song_{i+1}.mid")
```

## Development

### Running Tests

```bash
poetry run pytest
```

### Code Quality

```bash
# Format code
poetry run black llm_midi/

# Type checking (if mypy is added)
poetry run mypy llm_midi/

# Linting (if ruff is added)
poetry run ruff llm_midi/
```

### Adding New Features

The modular architecture makes it easy to extend:

1. **New music generators**: Extend `MidiGenerator` or create new generators
2. **Additional AI providers**: Implement new clients following `LLMClient` interface
3. **Music theory features**: Add functions to `utils/music_theory.py`
4. **Output formats**: Create new generators for different audio formats

## Troubleshooting

### Common Issues

**API Key not found**
```
ValueError: ANTHROPIC_API_KEY environment variable must be set
```
Solution: Set your API key in environment variables or .env file

**Invalid chord progression**
```
ParseError: Invalid chord progression structure
```
Solution: Enable debug mode (`--debug`) to see detailed parsing information

**MIDI generation fails**
```
ValueError: No chords provided
```
Solution: Check that AI response parsing succeeded; try different AI parameters

### Debug Mode

Enable detailed logging to troubleshoot issues:
```bash
llm-midi --debug --log-dir ./logs
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes following the existing architecture
4. Add tests for new functionality
5. Submit a pull request

## License

[Add your license here]

## Acknowledgments

- Built with [Anthropic's Claude AI](https://www.anthropic.com/)
- MIDI handling via [mido](https://mido.readthedocs.io/)
- Inspired by the intersection of AI and music creativity
