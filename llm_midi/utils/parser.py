"""Response parser utilities for Claude API responses."""

import ast
import logging
import re
from typing import List, Tuple, Union, Optional

from .music_theory import validate_chord_progression, validate_melody_patterns

logger = logging.getLogger(__name__)


class ParseError(Exception):
    """Exception raised when parsing fails."""
    pass


class ResponseParser:
    """Parser for Claude API responses containing musical data."""

    @staticmethod
    def extract_text_content(response: Union[str, List, object]) -> str:
        """
        Extract text content from various response formats.

        Args:
            response: Response from Claude API (can be string, list, or object)

        Returns:
            Extracted text content

        Raises:
            ParseError: If text content cannot be extracted
        """
        try:
            # If it's already a string, return it
            if isinstance(response, str):
                return response

            # If it's a list with TextBlock objects (anthropic format)
            if isinstance(response, list) and len(response) > 0:
                if hasattr(response[0], 'text'):
                    return getattr(response[0], 'text')
                elif isinstance(response[0], str):
                    return response[0]

            # If it's an object with text attribute
            if hasattr(response, 'text'):
                return getattr(response, 'text')

            # If it's an object with content attribute that contains text
            if hasattr(response, 'content'):
                content = getattr(response, 'content')
                if content and isinstance(content, list) and len(content) > 0:
                    if hasattr(content[0], 'text'):
                        return getattr(content[0], 'text')

            raise ParseError(f"Unknown response format: {type(response)}")

        except Exception as e:
            logger.error(f"Failed to extract text content: {e}")
            raise ParseError(f"Could not extract text from response: {e}")

    @staticmethod
    def parse_python_code(text_content: str) -> Tuple[List[Tuple[str, List[int]]], List[List[int]]]:
        """
        Parse Python code containing chords and melody patterns.

        Args:
            text_content: Raw text content containing Python variable assignments

        Returns:
            Tuple of (chords, melody_patterns)

        Raises:
            ParseError: If parsing fails
        """
        try:
            # Clean up the text content
            text_content = text_content.strip()

            # Remove any markdown code block markers
            text_content = re.sub(r'^```python\s*\n?', '', text_content, flags=re.MULTILINE)
            text_content = re.sub(r'^```\s*$', '', text_content, flags=re.MULTILINE)
            text_content = text_content.strip()

            # Find variable assignments using a bracket-matching approach
            chords_data = ResponseParser._extract_assignment(text_content, 'chords')
            patterns_data = ResponseParser._extract_assignment(text_content, 'melody_patterns')

            if not chords_data:
                raise ParseError("Could not find 'chords' assignment in response")

            if not patterns_data:
                raise ParseError("Could not find 'melody_patterns' assignment in response")

            # Parse the assignments
            try:
                chords_list = ast.literal_eval(chords_data)
                melody_patterns_list = ast.literal_eval(patterns_data)
            except (ValueError, SyntaxError) as e:
                raise ParseError(f"Invalid Python syntax in response: {e}")

            return chords_list, melody_patterns_list

        except ParseError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error during parsing: {e}")
            raise ParseError(f"Failed to parse response: {e}")

    @staticmethod
    def _extract_assignment(text: str, var_name: str) -> Optional[str]:
        """
        Extract a variable assignment with proper bracket matching.

        Args:
            text: Text content to search
            var_name: Variable name to find

        Returns:
            The extracted assignment value or None if not found
        """
        pattern = rf'{var_name}\s*=\s*\['
        match = re.search(pattern, text)
        if not match:
            return None

        start_pos = match.end() - 1  # Position of the opening bracket
        bracket_count = 1
        pos = start_pos + 1

        while pos < len(text) and bracket_count > 0:
            if text[pos] == '[':
                bracket_count += 1
            elif text[pos] == ']':
                bracket_count -= 1
            pos += 1

        if bracket_count == 0:
            return text[start_pos:pos]
        else:
            return None

    @staticmethod
    def parse_fallback_format(text_content: str) -> Tuple[List[Tuple[str, List[int]]], List[List[int]]]:
        """
        Fallback parser for alternative response formats.

        Args:
            text_content: Raw text content

        Returns:
            Tuple of (chords, melody_patterns)

        Raises:
            ParseError: If parsing fails
        """
        try:
            # Try splitting by double newlines (original approach)
            parts = text_content.split('\n\n')
            if len(parts) >= 2:
                chords_str = parts[0]
                melody_patterns_str = parts[1]

                # Extract assignments
                if '=' in chords_str:
                    chords_list = ast.literal_eval(chords_str.split('=')[1].strip())
                else:
                    raise ParseError("No assignment found in chords section")

                if '=' in melody_patterns_str:
                    melody_patterns_list = ast.literal_eval(melody_patterns_str.split('=')[1].strip())
                else:
                    raise ParseError("No assignment found in melody patterns section")

                return chords_list, melody_patterns_list

            raise ParseError("Could not split response into chords and melody patterns")

        except ParseError:
            raise
        except Exception as e:
            logger.error(f"Fallback parsing failed: {e}")
            raise ParseError(f"Fallback parsing failed: {e}")

    @classmethod
    def parse_response(
        cls,
        response: Union[str, List, object],
        validate: bool = True
    ) -> Tuple[List[Tuple[str, List[int]]], List[List[int]]]:
        """
        Parse Claude API response containing musical data.

        Args:
            response: Response from Claude API
            validate: Whether to validate the parsed data

        Returns:
            Tuple of (chords, melody_patterns)

        Raises:
            ParseError: If parsing or validation fails
        """
        # Extract text content
        text_content = cls.extract_text_content(response)
        logger.debug(f"Extracted text content: {text_content[:200]}...")

        # Try primary parsing method
        try:
            chords, melody_patterns = cls.parse_python_code(text_content)
            logger.info("Successfully parsed response using primary method")
        except ParseError as e:
            logger.warning(f"Primary parsing failed: {e}")
            # Try fallback method
            try:
                chords, melody_patterns = cls.parse_fallback_format(text_content)
                logger.info("Successfully parsed response using fallback method")
            except ParseError as fallback_error:
                logger.error(f"All parsing methods failed. Primary: {e}, Fallback: {fallback_error}")
                raise ParseError(f"All parsing methods failed. Last error: {fallback_error}")

        # Validate the parsed data if requested
        if validate:
            if not validate_chord_progression(chords):
                raise ParseError("Invalid chord progression structure")

            if not validate_melody_patterns(melody_patterns):
                raise ParseError("Invalid melody patterns structure")

            logger.info("Parsed data validated successfully")

        logger.info(f"Parsed {len(chords)} chords and {len(melody_patterns)} melody patterns")
        return chords, melody_patterns


# Convenience function for backwards compatibility
def parse_response(
    response: Union[str, List, object],
    validate: bool = True
) -> Tuple[List[Tuple[str, List[int]]], List[List[int]]]:
    """
    Parse Claude API response containing musical data.

    Args:
        response: Response from Claude API
        validate: Whether to validate the parsed data

    Returns:
        Tuple of (chords, melody_patterns)

    Raises:
        ParseError: If parsing or validation fails
    """
    return ResponseParser.parse_response(response, validate)
