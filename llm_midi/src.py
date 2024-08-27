import ast
import os
import random
from typing import List, Tuple, Union

import anthropic
import mido
from mido import Message, MidiFile, MidiTrack


def get_chords_from_claude() -> str:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("API key not found in environment variables.")
    client = anthropic.Anthropic(api_key=api_key)

    system_message = """You are a sophisticated AI music assistant with expertise in music theory, composition, and MIDI. Your task is to generate musically coherent and interesting chord progressions and melody patterns. When prompted, you will:

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

    message = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=1000,
        temperature=0.7,
        system=system_message,
        messages=[
            {
                "role": "user",
                "content": """Generate a set of chords and melody patterns for a song with the following specifications:

                - A list of chords, each represented as a tuple containing:
                  * The chord name as a string
                  * A list of three MIDI note numbers representing the notes in the chord
                - The number of chords should be random, between 5 and 10.
                - A list of melody patterns, each represented as a list of integers.
                - The number of melody patterns should be random, between 3 and 6.
                - Each melody pattern should have a random length between 4 and 12 notes.

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
                Ensure that the chords and melody patterns are musically coherent and complex. The key and style are up to you - be creative!""",
            }
        ],
    )
    return message.content


def parse_response(
    response: str,
) -> Tuple[List[Tuple[str, List[int]]], List[List[int]]]:
    # Extract the text content from the TextBlock
    text_content = response[0].text
    # Split the content into chords and melody patterns
    chords_str, melody_patterns_str = text_content.split("\n\n")
    # Parse chords
    chords_list = ast.literal_eval(chords_str.split("=")[1].strip())
    # Parse melody patterns
    melody_patterns_list = ast.literal_eval(melody_patterns_str.split("=")[1].strip())
    return chords_list, melody_patterns_list


def create_evolved_melody(
    chords: List[Tuple[str, List[int]]], melody_patterns: List[List[int]]
) -> MidiFile:
    midi = MidiFile()
    track = MidiTrack()
    midi.tracks.append(track)
    # Set tempo to 120 BPM

    track.append(Message("program_change", program=0, channel=0, time=0))  # Piano
    tempo = mido.bpm2tempo(120)
    track.append(mido.MetaMessage("set_tempo", tempo=tempo))

    ticks_per_beat = 480
    beats_per_bar = 4

    for chord_name, chord_notes in chords:
        base_note = chord_notes[0]

        for _ in range(2):  # Play each chord for 2 bars
            # Play the chord
            for note in chord_notes:
                track.append(Message("note_on", note=note, velocity=64, time=0))

            # Generate melody for this bar
            pattern = random.choice(melody_patterns)
            for offset in pattern:
                melody_note = base_note + offset
                duration = random.choice([ticks_per_beat // 2, ticks_per_beat // 4])
                track.append(Message("note_on", note=melody_note, velocity=80, time=0))
                track.append(
                    Message("note_off", note=melody_note, velocity=0, time=duration)
                )

            # Turn off chord notes at the end of the bar
            for note in chord_notes:
                track.append(Message("note_off", note=note, velocity=0, time=0))

    return midi


def generate_song_name() -> str:
    adjectives = [
        "Midnight",
        "Neon",
        "Velvet",
        "Crystal",
        "Savage",
        "Electric",
        "Cosmic",
        "Whispered",
        "Thunderous",
        "Silken",
        "loving",
        "Vibrant",
        "Serene",
        "Enigmatic",
        "Tenacious",
        "Whimsical",
    ]

    nouns = [
        "Dream",
        "Heart",
        "City",
        "Love",
        "Shadow",
        "Storm",
        "Melody",
        "Rhythm",
        "Whisper",
        "Echo",
        "Telescope",
        "Avalanche",
        "Citadel",
        "Butterfly",
        "Symphony",
    ]
    verbs = [
        "Dancing",
        "Falling",
        "Rising",
        "Echoing",
        "Shimmering",
        "Fading",
        "Pulsing",
        "Soaring",
        "Crashing",
        "Burning",
    ]
    emotions = [
        "Joy",
        "Sorrow",
        "Passion",
        "Desire",
        "Rage",
        "Bliss",
        "Longing",
        "Hope",
        "Fear",
        "Wonder",
    ]

    patterns = [
        f"{random.choice(adjectives)} {random.choice(nouns)}",
        f"The {random.choice(adjectives)} {random.choice(nouns)}",
        f"{random.choice(verbs)} {random.choice(nouns)}",
        f"{random.choice(nouns)} of {random.choice(emotions)}",
        f"{random.choice(adjectives)} {random.choice(verbs)}",
        f"{random.choice(emotions)} in {random.choice(adjectives)} {random.choice(nouns)}",
        f"{random.choice(verbs)} to the {random.choice(adjectives)} {random.choice(nouns)}",
        f"{random.choice(adjectives)} {random.choice(nouns)} {random.choice(verbs)}",
    ]

    return random.choice(patterns)


def main():
    try:
        response = get_chords_from_claude()
        chords, melody_patterns = parse_response(response)
        midi = create_evolved_melody(chords, melody_patterns)
        output_path = f"{generate_song_name()}.mid"
        midi.save(output_path)
        print(f"MIDI file saved as {output_path}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        import traceback

        print("Traceback:")
        print(traceback.format_exc())


if __name__ == "__main__":
    main()
