"""Command-line interface for llm_midi."""

import argparse
import sys
from pathlib import Path
from typing import Optional

from .core.config import AppConfig, AIConfig, MusicConfig
from .core.llm_client import LLMClient
from .core.midi_generator import MidiGenerator, generate_song_name
from .utils.logging import setup_app_logging, get_logger
from .utils.parser import ResponseParser, ParseError

logger = get_logger(__name__)


def create_parser() -> argparse.ArgumentParser:
    """Create the command-line argument parser."""
    parser = argparse.ArgumentParser(
        prog="llm-midi",
        description="Generate MIDI files using AI-powered chord progressions and melodies",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  llm-midi                              # Generate with default settings
  llm-midi -o my_song.mid               # Specify output filename
  llm-midi --chords 8 --patterns 5     # Custom number of chords and patterns
  llm-midi --tempo 140 --debug         # Faster tempo with debug logging
  llm-midi --quiet                     # Suppress output except errors
        """
    )

    # Output options
    output_group = parser.add_argument_group("Output Options")
    output_group.add_argument(
        "-o", "--output",
        type=str,
        help="Output MIDI filename (default: auto-generated song name)"
    )
    output_group.add_argument(
        "--output-dir",
        type=Path,
        default=Path.cwd(),
        help="Output directory (default: current directory)"
    )

    # Music generation options
    music_group = parser.add_argument_group("Music Generation Options")
    music_group.add_argument(
        "--chords",
        type=int,
        metavar="N",
        help="Number of chords to generate (overrides AI randomization)"
    )
    music_group.add_argument(
        "--patterns",
        type=int,
        metavar="N",
        help="Number of melody patterns to generate (overrides AI randomization)"
    )
    music_group.add_argument(
        "--tempo",
        type=int,
        default=120,
        metavar="BPM",
        help="Tempo in beats per minute (default: 120)"
    )
    music_group.add_argument(
        "--bars-per-chord",
        type=int,
        default=2,
        metavar="N",
        help="Number of bars per chord (default: 2)"
    )

    # AI options
    ai_group = parser.add_argument_group("AI Options")
    ai_group.add_argument(
        "--model",
        type=str,
        default="claude-3-opus-20240229",
        help="Claude model to use (default: claude-3-opus-20240229)"
    )
    ai_group.add_argument(
        "--temperature",
        type=float,
        default=0.7,
        metavar="T",
        help="AI temperature for creativity (0.0-1.0, default: 0.7)"
    )
    ai_group.add_argument(
        "--max-tokens",
        type=int,
        default=1000,
        metavar="N",
        help="Maximum tokens for AI response (default: 1000)"
    )

    # Logging options
    logging_group = parser.add_argument_group("Logging Options")
    logging_group.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    logging_group.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress output except errors"
    )
    logging_group.add_argument(
        "--log-dir",
        type=Path,
        help="Directory for log files"
    )

    # Utility options
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Generate musical content but don't create MIDI file"
    )

    return parser


def validate_args(args: argparse.Namespace) -> None:
    """Validate command-line arguments."""
    if args.temperature < 0.0 or args.temperature > 1.0:
        raise ValueError("Temperature must be between 0.0 and 1.0")

    if args.tempo <= 0:
        raise ValueError("Tempo must be positive")

    if args.bars_per_chord <= 0:
        raise ValueError("Bars per chord must be positive")

    if args.max_tokens <= 0:
        raise ValueError("Max tokens must be positive")

    if args.chords is not None and args.chords <= 0:
        raise ValueError("Number of chords must be positive")

    if args.patterns is not None and args.patterns <= 0:
        raise ValueError("Number of patterns must be positive")

    # Ensure output directory exists
    args.output_dir.mkdir(parents=True, exist_ok=True)


def create_config(args: argparse.Namespace) -> AppConfig:
    """Create application configuration from command-line arguments."""
    music_config = MusicConfig(
        tempo_bpm=args.tempo,
        bars_per_chord=args.bars_per_chord
    )

    # Override min/max values if specific counts are requested
    if args.chords is not None:
        music_config.min_chords = args.chords
        music_config.max_chords = args.chords

    if args.patterns is not None:
        music_config.min_melody_patterns = args.patterns
        music_config.max_melody_patterns = args.patterns

    ai_config = AIConfig(
        model=args.model,
        temperature=args.temperature,
        max_tokens=args.max_tokens
    )

    return AppConfig(music=music_config, ai=ai_config)


def generate_filename(args: argparse.Namespace) -> Path:
    """Generate output filename."""
    if args.output:
        filename = args.output
        if not filename.endswith('.mid'):
            filename += '.mid'
    else:
        song_name = generate_song_name()
        filename = f"{song_name}.mid"

    return args.output_dir / filename


def main(argv: Optional[list] = None) -> int:
    """Main entry point for the CLI."""
    parser = create_parser()
    args = parser.parse_args(argv)

    # Set up logging
    setup_app_logging(
        debug=args.debug,
        log_dir=args.log_dir,
        quiet=args.quiet
    )

    try:
        # Validate arguments
        validate_args(args)

        # Create configuration
        config = create_config(args)

        logger.info("Starting MIDI generation")
        logger.debug(f"Configuration: Music={config.music}, AI={config.ai}")

        # Generate musical content
        client = LLMClient(config.ai)
        response = client.generate_musical_content(
            min_chords=config.music.min_chords,
            max_chords=config.music.max_chords,
            min_patterns=config.music.min_melody_patterns,
            max_patterns=config.music.max_melody_patterns,
            min_pattern_length=config.music.min_pattern_length,
            max_pattern_length=config.music.max_pattern_length
        )

        # Parse the response
        chords, melody_patterns = ResponseParser.parse_response(response)

        logger.info(f"Generated {len(chords)} chords and {len(melody_patterns)} melody patterns")

        if not args.quiet:
            print(f"Generated musical content:")
            print(f"  Chords: {len(chords)}")
            print(f"  Melody patterns: {len(melody_patterns)}")

            # Show chord names
            chord_names = [name for name, _ in chords]
            print(f"  Chord progression: {' - '.join(chord_names)}")

        # Generate MIDI file (unless dry run)
        if not args.dry_run:
            generator = MidiGenerator(config.music)
            midi_file = generator.create_midi_file(chords, melody_patterns)

            # Save the file
            output_path = generate_filename(args)
            midi_file.save(str(output_path))

            if not args.quiet:
                print(f"MIDI file saved as: {output_path}")

            logger.info(f"MIDI file saved to {output_path}")
        else:
            logger.info("Dry run completed - no MIDI file generated")
            if not args.quiet:
                print("Dry run completed - no MIDI file generated")

        return 0

    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        if not args.quiet:
            print("\nOperation cancelled by user")
        return 1

    except ParseError as e:
        logger.error(f"Failed to parse AI response: {e}")
        if not args.quiet:
            print(f"Error: Failed to parse AI response - {e}", file=sys.stderr)
        return 1

    except ValueError as e:
        logger.error(f"Invalid configuration: {e}")
        if not args.quiet:
            print(f"Error: {e}", file=sys.stderr)
        return 1

    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=args.debug)
        if not args.quiet:
            if args.debug:
                print(f"Error: {e}", file=sys.stderr)
                import traceback
                traceback.print_exc()
            else:
                print(f"Error: {e}", file=sys.stderr)
                print("Use --debug for more detailed error information", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
