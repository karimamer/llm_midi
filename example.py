#!/usr/bin/env python3
"""
Example script demonstrating the llm_midi refactored API.

This script shows various ways to use the llm_midi package for generating
MIDI files with AI-powered chord progressions and melodies.
"""

import os
import sys
from pathlib import Path

# Add the package to path for development
sys.path.insert(0, str(Path(__file__).parent))

from llm_midi import (
    main, LLMClient, MidiGenerator, ResponseParser,
    MusicConfig, AIConfig, AppConfig,
    generate_song_name, create_midi_file,
    get_chord_notes, validate_chord_progression, validate_melody_patterns,
    setup_app_logging, get_logger
)
from llm_midi.utils.parser import ParseError


def example_basic_usage():
    """Demonstrate basic usage of the llm_midi package."""
    print("=== Basic Usage Example ===")

    # Simple way - just generate a MIDI file
    print("Generating MIDI file with default settings...")
    try:
        exit_code = main(output_path="basic_example.mid")
        if exit_code == 0:
            print("✓ Successfully generated basic_example.mid")
        else:
            print("✗ Failed to generate MIDI file")
    except Exception as e:
        print(f"✗ Error: {e}")

    print()


def example_custom_configuration():
    """Demonstrate custom configuration usage."""
    print("=== Custom Configuration Example ===")

    # Check if API key is available
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("⚠ ANTHROPIC_API_KEY not set, skipping AI-powered examples")
        return

    try:
        # Create custom configurations
        music_config = MusicConfig(
            tempo_bpm=140,          # Faster tempo
            bars_per_chord=4,       # Longer chord sections
            min_chords=6,           # More chords
            max_chords=8,
            chord_velocity=70,      # Louder chords
            melody_velocity=90      # Louder melody
        )

        ai_config = AIConfig(
            temperature=0.8,        # More creative
            max_tokens=1200         # Allow longer responses
        )

        config = AppConfig(music=music_config, ai=ai_config)

        print(f"Configuration:")
        print(f"  Tempo: {config.music.tempo_bpm} BPM")
        print(f"  Chords: {config.music.min_chords}-{config.music.max_chords}")
        print(f"  AI Temperature: {config.ai.temperature}")

        # Generate using custom config
        client = LLMClient(config.ai)
        print("Generating musical content with custom settings...")

        response = client.generate_musical_content(
            min_chords=config.music.min_chords,
            max_chords=config.music.max_chords,
            min_patterns=config.music.min_melody_patterns,
            max_patterns=config.music.max_melody_patterns
        )

        # Parse response
        chords, patterns = ResponseParser.parse_response(response)
        print(f"✓ Generated {len(chords)} chords and {len(patterns)} melody patterns")

        # Show chord progression
        chord_names = [name for name, _ in chords]
        print(f"  Chord progression: {' → '.join(chord_names)}")

        # Create MIDI file
        generator = MidiGenerator(config.music)
        midi_file = generator.create_midi_file(chords, patterns)

        song_name = generate_song_name()
        output_path = f"custom_{song_name}.mid"
        midi_file.save(output_path)
        print(f"✓ Saved as {output_path}")

    except ParseError as e:
        print(f"✗ Failed to parse AI response: {e}")
    except Exception as e:
        print(f"✗ Error: {e}")

    print()


def example_manual_chord_progression():
    """Demonstrate creating MIDI from manual chord progressions."""
    print("=== Manual Chord Progression Example ===")

    try:
        # Create a classic I-V-vi-IV progression in C major
        chords = [
            ("C", get_chord_notes("C", 4)),    # I
            ("G", get_chord_notes("G", 4)),    # V
            ("Am", get_chord_notes("Am", 4)),  # vi
            ("F", get_chord_notes("F", 4))     # IV
        ]

        # Create some melody patterns
        patterns = [
            [0, 2, 4, 2, 0, -2, 0, 2],         # Rising and falling
            [4, 2, 0, 2, 4, 6, 4, 2],          # Arpeggiated
            [0, -2, 0, 2, 4, 2, 0, -2],        # Wave pattern
            [-4, -2, 0, 2, 4, 2, 0, -2]        # Ascending from below
        ]

        # Validate the data
        if not validate_chord_progression(chords):
            print("✗ Invalid chord progression")
            return

        if not validate_melody_patterns(patterns):
            print("✗ Invalid melody patterns")
            return

        print("Creating MIDI from manual chord progression:")
        print(f"  Chords: {' → '.join([name for name, _ in chords])}")
        print(f"  Patterns: {len(patterns)} melody patterns")

        # Generate MIDI using convenience function
        midi_file = create_midi_file(chords, patterns)
        midi_file.save("manual_progression.mid")
        print("✓ Saved as manual_progression.mid")

    except Exception as e:
        print(f"✗ Error: {e}")

    print()


def example_batch_generation():
    """Demonstrate generating multiple MIDI files in batch."""
    print("=== Batch Generation Example ===")

    if not os.getenv("ANTHROPIC_API_KEY"):
        print("⚠ ANTHROPIC_API_KEY not set, skipping batch generation")
        return

    try:
        config = AppConfig()
        client = LLMClient(config.ai)
        generator = MidiGenerator(config.music)

        # Create output directory
        output_dir = Path("batch_output")
        output_dir.mkdir(exist_ok=True)

        num_songs = 3
        print(f"Generating {num_songs} MIDI files...")

        for i in range(num_songs):
            print(f"  Generating song {i+1}/{num_songs}...")

            try:
                # Generate content
                response = client.generate_musical_content()
                chords, patterns = ResponseParser.parse_response(response)

                # Create MIDI
                midi_file = generator.create_midi_file(chords, patterns)

                # Save with generated name
                song_name = generate_song_name()
                output_path = output_dir / f"{song_name}.mid"
                midi_file.save(str(output_path))

                chord_names = [name for name, _ in chords]
                print(f"    ✓ {song_name}: {' → '.join(chord_names)}")

            except Exception as e:
                print(f"    ✗ Failed to generate song {i+1}: {e}")

        print(f"✓ Batch generation complete. Files saved in {output_dir}/")

    except Exception as e:
        print(f"✗ Batch generation failed: {e}")

    print()


def example_error_handling():
    """Demonstrate proper error handling."""
    print("=== Error Handling Example ===")

    # Example 1: Invalid configuration
    try:
        config = MusicConfig(tempo_bpm=-1)  # Invalid tempo
    except ValueError as e:
        print(f"✓ Caught invalid configuration: {e}")

    # Example 2: Missing API key
    try:
        # Temporarily remove API key
        original_key = os.environ.get("ANTHROPIC_API_KEY")
        if "ANTHROPIC_API_KEY" in os.environ:
            del os.environ["ANTHROPIC_API_KEY"]

        config = AIConfig()
    except ValueError as e:
        print(f"✓ Caught missing API key: {e}")
        # Restore API key
        if original_key:
            os.environ["ANTHROPIC_API_KEY"] = original_key

    # Example 3: Invalid MIDI generation
    try:
        config = MusicConfig()
        generator = MidiGenerator(config)
        generator.create_midi_file([], [])  # Empty data
    except ValueError as e:
        print(f"✓ Caught invalid MIDI generation: {e}")

    print()


def example_logging_and_debugging():
    """Demonstrate logging and debugging features."""
    print("=== Logging and Debugging Example ===")

    # Set up logging
    setup_app_logging(debug=True, log_dir="example_logs")
    logger = get_logger(__name__)

    logger.info("This is an info message")
    logger.debug("This is a debug message")
    logger.warning("This is a warning message")

    print("✓ Logging configured - check example_logs/ for log files")
    print()


def main_example():
    """Run all examples."""
    print("LLM MIDI - Refactored API Examples")
    print("=" * 50)
    print()

    # Check for API key
    api_key_available = bool(os.getenv("ANTHROPIC_API_KEY"))
    if not api_key_available:
        print("⚠ Warning: ANTHROPIC_API_KEY not found in environment")
        print("  Some examples requiring AI will be skipped")
        print("  Set your API key: export ANTHROPIC_API_KEY='your-key-here'")
        print()

    # Run examples
    example_basic_usage()
    example_custom_configuration()
    example_manual_chord_progression()
    example_batch_generation()
    example_error_handling()
    example_logging_and_debugging()

    print("=" * 50)
    print("Examples completed!")

    # Show generated files
    generated_files = [
        "basic_example.mid",
        "manual_progression.mid"
    ]

    # Add custom generated files
    for file in Path(".").glob("custom_*.mid"):
        generated_files.append(str(file))

    # Add batch files
    batch_dir = Path("batch_output")
    if batch_dir.exists():
        for file in batch_dir.glob("*.mid"):
            generated_files.append(str(file))

    existing_files = [f for f in generated_files if Path(f).exists()]
    if existing_files:
        print(f"\nGenerated MIDI files:")
        for file in existing_files:
            size = Path(file).stat().st_size
            print(f"  {file} ({size} bytes)")


if __name__ == "__main__":
    main_example()
