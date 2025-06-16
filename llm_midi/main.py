"""Main entry point for the llm_midi package."""

import logging
import sys
import traceback
from pathlib import Path
from typing import Optional

from .core.config import get_config
from .core.llm_client import LLMClient
from .core.midi_generator import MidiGenerator, generate_song_name
from .utils.logging import setup_app_logging, get_logger
from .utils.parser import ResponseParser, ParseError

logger = get_logger(__name__)


def main(output_path: Optional[str] = None, debug: bool = False) -> int:
    """
    Main function to generate a MIDI file using AI-generated musical content.

    Args:
        output_path: Optional path for the output MIDI file
        debug: Enable debug logging

    Returns:
        Exit code (0 for success, 1 for error)
    """
    # Set up logging
    setup_app_logging(debug=debug)

    try:
        logger.info("Starting MIDI generation process")

        # Get configuration
        config = get_config()
        logger.debug(f"Configuration loaded: Music={config.music}, AI={config.ai}")

        # Initialize LLM client
        logger.info("Initializing AI client")
        client = LLMClient(config.ai)

        # Generate musical content from Claude
        logger.info("Requesting musical content from AI")
        response = client.generate_musical_content(
            min_chords=config.music.min_chords,
            max_chords=config.music.max_chords,
            min_patterns=config.music.min_melody_patterns,
            max_patterns=config.music.max_melody_patterns,
            min_pattern_length=config.music.min_pattern_length,
            max_pattern_length=config.music.max_pattern_length
        )

        # Parse the response
        logger.info("Parsing AI response")
        chords, melody_patterns = ResponseParser.parse_response(response)

        logger.info(f"Successfully parsed {len(chords)} chords and {len(melody_patterns)} melody patterns")

        # Generate MIDI file
        logger.info("Generating MIDI composition")
        generator = MidiGenerator(config.music)
        midi_file = generator.create_midi_file(chords, melody_patterns)

        # Determine output filename
        if output_path is None:
            song_name = generate_song_name()
            output_path = f"{song_name}.mid"

        # Ensure output path has .mid extension
        if not output_path.endswith('.mid'):
            output_path += '.mid'

        # Save the MIDI file
        logger.info(f"Saving MIDI file to {output_path}")
        midi_file.save(output_path)

        print(f"MIDI file saved as {output_path}")
        logger.info("MIDI generation completed successfully")

        return 0

    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        print("\nOperation cancelled by user")
        return 1

    except ParseError as e:
        logger.error(f"Failed to parse AI response: {e}")
        print(f"Error: Failed to parse AI response - {e}", file=sys.stderr)
        return 1

    except ValueError as e:
        logger.error(f"Configuration or validation error: {e}")
        print(f"Error: {e}", file=sys.stderr)
        return 1

    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=debug)
        print(f"An error occurred: {str(e)}", file=sys.stderr)

        if debug:
            print("Traceback:", file=sys.stderr)
            traceback.print_exc()
        else:
            print("Use debug=True for detailed error information", file=sys.stderr)

        return 1


if __name__ == "__main__":
    # Simple command-line interface for direct execution
    import argparse

    parser = argparse.ArgumentParser(description="Generate MIDI files using AI")
    parser.add_argument("-o", "--output", help="Output MIDI filename")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    args = parser.parse_args()

    exit_code = main(output_path=args.output, debug=args.debug)
    sys.exit(exit_code)
