import logging
import anthropic

from .config import AIConfig

logger = logging.getLogger(__name__)


class LLMClient:
    """Client for interacting with Claude API to generate musical content."""

    def __init__(self, config: AIConfig):
        """Initialize the LLM client with configuration."""
        self.config = config
        self.client = anthropic.Anthropic(api_key=config.api_key)

        self.system_message = """You are a sophisticated AI music assistant with expertise in music theory, composition, and MIDI. Your task is to generate musically coherent and interesting chord progressions and melody patterns. When prompted, you will:

1. Create a list of chords, where each chord is represented as a tuple containing:
   - The chord name as a string
   - A list of three MIDI note numbers representing the notes in the chord

2. Generate a list of melody patterns, where each pattern is a list of integers representing relative pitch movements in semitones.

3. Ensure musical coherence and complexity in your generated content.

4. Adhere strictly to the output format specified in the user's request.

5. Be creative with key signatures, chord voicings, and melodic structures while maintaining musical logic.

6. Provide your output as valid Python code that can be directly executed or parsed.

7. Return ONLY the requested Python code without any additional explanations or text.

Remember, your goal is to create musically interesting and varied output each time you're prompted, suitable for inspiring musicians or for use in computational music applications."""

    def generate_musical_content(
        self,
        min_chords: int = 5,
        max_chords: int = 10,
        min_patterns: int = 3,
        max_patterns: int = 6,
        min_pattern_length: int = 4,
        max_pattern_length: int = 12
    ) -> str:
        """
        Generate chord progressions and melody patterns from Claude.

        Args:
            min_chords: Minimum number of chords to generate
            max_chords: Maximum number of chords to generate
            min_patterns: Minimum number of melody patterns
            max_patterns: Maximum number of melody patterns
            min_pattern_length: Minimum length of each melody pattern
            max_pattern_length: Maximum length of each melody pattern

        Returns:
            Raw response text from Claude containing Python code

        Raises:
            anthropic.APIError: If API call fails
            ValueError: If response is invalid
        """
        user_message = f"""Generate a set of chords and melody patterns for a song with the following specifications:

                - A list of chords, each represented as a tuple containing:
                  * The chord name as a string
                  * A list of three MIDI note numbers representing the notes in the chord
                - The number of chords should be random, between {min_chords} and {max_chords}.
                - A list of melody patterns, each represented as a list of integers.
                - The number of melody patterns should be random, between {min_patterns} and {max_patterns}.
                - Each melody pattern should have a random length between {min_pattern_length} and {max_pattern_length} notes.

                Please format the output exactly as follows:
                chords = [
                    ("F#m", [54, 57, 61]),  # F#, A, C#
                    ("D", [50, 54, 57]),    # D, F#, A
                    ("A", [45, 49, 52]),    # A, C#, E
                    ("E", [52, 56, 59]),    # E, G#, B
                    ("Bm", [47, 50, 54]),   # B, D, F#
                    ("G#m", [56, 59, 63]),  # G#, B, D#
                    ("C#m", [49, 52, 56])   # C#, E, G#
                ]
                melody_patterns = [
                    [0, 2, 4, 2, 0, -2, 0, 2],
                    [4, 2, 0, 2, 4, 6, 4, 2],
                    [0, -2, 0, 2, 4, 2, 0, -2],
                    [-4, -2, 0, 2, 4, 2, 0, -2]
                ]
                Ensure that the chords and melody patterns are musically coherent and complex. The key and style are up to you - be creative!"""

        try:
            logger.info("Requesting musical content from Claude API")
            message = self.client.messages.create(
                model=self.config.model,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                system=self.system_message,
                messages=[{"role": "user", "content": user_message}]
            )

            if not message.content:
                raise ValueError("Empty response from Claude API")

            logger.info("Successfully received musical content from Claude API")
            # Extract text content from the response
            if isinstance(message.content, list) and len(message.content) > 0:
                return message.content[0].text
            elif hasattr(message.content, 'text'):
                return message.content.text
            else:
                return str(message.content)

        except anthropic.APIError as e:
            logger.error(f"Claude API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during API call: {e}")
            raise ValueError(f"Failed to generate musical content: {e}")
