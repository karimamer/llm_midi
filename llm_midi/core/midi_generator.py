"""MIDI generation module for creating musical compositions."""

import logging
import random
from typing import List, Tuple, Optional

import mido  # type: ignore
from mido import Message, MidiFile, MidiTrack  # type: ignore

from .config import MusicConfig

logger = logging.getLogger(__name__)


class MidiGenerator:
    """Generates MIDI files from chord progressions and melody patterns."""

    def __init__(self, config: MusicConfig):
        """Initialize the MIDI generator with configuration."""
        self.config = config

    def create_midi_file(
        self,
        chords: List[Tuple[str, List[int]]],
        melody_patterns: List[List[int]]
    ) -> MidiFile:
        """
        Create a MIDI file from chord progressions and melody patterns.

        Args:
            chords: List of (chord_name, midi_notes) tuples
            melody_patterns: List of melody patterns (lists of intervals)

        Returns:
            Generated MIDI file

        Raises:
            ValueError: If input data is invalid
        """
        if not chords:
            raise ValueError("No chords provided")

        if not melody_patterns:
            raise ValueError("No melody patterns provided")

        logger.info(f"Generating MIDI with {len(chords)} chords and {len(melody_patterns)} melody patterns")

        midi = MidiFile()
        track = MidiTrack()
        midi.tracks.append(track)

        # Set up track with tempo and instrument
        self._setup_track(track)

        # Generate the composition
        self._generate_composition(track, chords, melody_patterns)

        logger.info("MIDI file generated successfully")
        return midi

    def _setup_track(self, track: MidiTrack) -> None:
        """Set up the MIDI track with initial settings."""
        # Set instrument to piano
        track.append(Message("program_change", program=0, channel=0, time=0))

        # Set tempo
        tempo = mido.bpm2tempo(self.config.tempo_bpm)
        track.append(mido.MetaMessage("set_tempo", tempo=tempo))

    def _generate_composition(
        self,
        track: MidiTrack,
        chords: List[Tuple[str, List[int]]],
        melody_patterns: List[List[int]]
    ) -> None:
        """Generate the full composition on the track."""
        for chord_name, chord_notes in chords:
            base_note = chord_notes[0]

            for bar in range(self.config.bars_per_chord):
                self._play_chord_and_melody(track, chord_notes, base_note, melody_patterns)

    def _play_chord_and_melody(
        self,
        track: MidiTrack,
        chord_notes: List[int],
        base_note: int,
        melody_patterns: List[List[int]]
    ) -> None:
        """Play a chord with melody for one bar."""
        # Start chord
        for note in chord_notes:
            track.append(Message("note_on", note=note, velocity=self.config.chord_velocity, time=0))

        # Generate melody for this bar
        pattern = random.choice(melody_patterns)
        self._generate_melody(track, base_note, pattern)

        # End chord
        for note in chord_notes:
            track.append(Message("note_off", note=note, velocity=0, time=0))

    def _generate_melody(self, track: MidiTrack, base_note: int, pattern: List[int]) -> None:
        """Generate melody from a pattern."""
        for offset in pattern:
            melody_note = base_note + offset

            # Ensure melody note is in valid MIDI range
            melody_note = max(0, min(127, melody_note))

            # Random note duration for variety
            duration = random.choice([
                self.config.ticks_per_beat // 2,
                self.config.ticks_per_beat // 4
            ])

            track.append(Message("note_on", note=melody_note, velocity=self.config.melody_velocity, time=0))
            track.append(Message("note_off", note=melody_note, velocity=0, time=duration))


class SongNameGenerator:
    """Generates creative song names."""

    def __init__(self):
        """Initialize the song name generator."""
        self.adjectives = [
            "Midnight", "Neon", "Velvet", "Crystal", "Savage", "Electric", "Cosmic",
            "Whispered", "Thunderous", "Silken", "Loving", "Vibrant", "Serene",
            "Enigmatic", "Tenacious", "Whimsical", "Ethereal", "Radiant", "Mystical",
            "Haunting", "Brilliant", "Dreamy", "Fierce", "Gentle", "Powerful"
        ]

        self.nouns = [
            "Dream", "Heart", "City", "Love", "Shadow", "Storm", "Melody", "Rhythm",
            "Whisper", "Echo", "Telescope", "Avalanche", "Citadel", "Butterfly",
            "Symphony", "River", "Mountain", "Ocean", "Star", "Moon", "Fire", "Rain",
            "Wind", "Light", "Darkness", "Journey", "Adventure", "Memory", "Hope"
        ]

        self.verbs = [
            "Dancing", "Falling", "Rising", "Echoing", "Shimmering", "Fading",
            "Pulsing", "Soaring", "Crashing", "Burning", "Flowing", "Glowing",
            "Sparkling", "Wandering", "Floating", "Spinning", "Drifting"
        ]

        self.emotions = [
            "Joy", "Sorrow", "Passion", "Desire", "Rage", "Bliss", "Longing",
            "Hope", "Fear", "Wonder", "Peace", "Chaos", "Serenity", "Excitement",
            "Melancholy", "Euphoria", "Tranquility"
        ]

        self.patterns = [
            lambda: f"{random.choice(self.adjectives)} {random.choice(self.nouns)}",
            lambda: f"The {random.choice(self.adjectives)} {random.choice(self.nouns)}",
            lambda: f"{random.choice(self.verbs)} {random.choice(self.nouns)}",
            lambda: f"{random.choice(self.nouns)} of {random.choice(self.emotions)}",
            lambda: f"{random.choice(self.adjectives)} {random.choice(self.verbs)}",
            lambda: f"{random.choice(self.emotions)} in {random.choice(self.adjectives)} {random.choice(self.nouns)}",
            lambda: f"{random.choice(self.verbs)} to the {random.choice(self.adjectives)} {random.choice(self.nouns)}",
            lambda: f"{random.choice(self.adjectives)} {random.choice(self.nouns)} {random.choice(self.verbs)}",
            lambda: f"When {random.choice(self.nouns)} {random.choice(self.verbs)}",
            lambda: f"{random.choice(self.emotions)} and {random.choice(self.emotions)}"
        ]

    def generate(self) -> str:
        """
        Generate a random song name.

        Returns:
            Generated song name
        """
        pattern = random.choice(self.patterns)
        return pattern()


# Convenience functions
def generate_song_name() -> str:
    """Generate a random song name."""
    generator = SongNameGenerator()
    return generator.generate()


def create_midi_file(
    chords: List[Tuple[str, List[int]]],
    melody_patterns: List[List[int]],
    config: Optional[MusicConfig] = None
) -> MidiFile:
    """
    Create a MIDI file from chord progressions and melody patterns.

    Args:
        chords: List of (chord_name, midi_notes) tuples
        melody_patterns: List of melody patterns (lists of intervals)
        config: Music configuration (uses default if None)

    Returns:
        Generated MIDI file
    """
    if config is None:
        config = MusicConfig()

    generator = MidiGenerator(config)
    return generator.create_midi_file(chords, melody_patterns)
