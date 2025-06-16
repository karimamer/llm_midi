import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class MusicConfig:
    """Configuration for music generation parameters."""
    tempo_bpm: int = 120
    ticks_per_beat: int = 480
    beats_per_bar: int = 4
    chord_velocity: int = 64
    melody_velocity: int = 80
    bars_per_chord: int = 2
    min_chords: int = 5
    max_chords: int = 10
    min_melody_patterns: int = 3
    max_melody_patterns: int = 6
    min_pattern_length: int = 4
    max_pattern_length: int = 12


@dataclass
class AIConfig:
    """Configuration for AI/LLM parameters."""
    model: str = "claude-3-opus-20240229"
    max_tokens: int = 1000
    temperature: float = 0.7
    api_key: Optional[str] = None

    def __post_init__(self):
        """Load API key from environment if not provided."""
        if self.api_key is None:
            self.api_key = os.getenv("ANTHROPIC_API_KEY")

        if not self.api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY environment variable must be set or "
                "api_key must be provided in configuration"
            )


@dataclass
class AppConfig:
    """Main application configuration."""
    music: MusicConfig = field(default_factory=MusicConfig)
    ai: AIConfig = field(default_factory=AIConfig)


def get_config() -> AppConfig:
    """Get application configuration with environment overrides."""
    return AppConfig()
