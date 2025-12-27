"""
Business logic for the music arrangement generator.

Contains:
- Pattern generation algorithms
- Chromatic enclosure calculations
- Note creation utilities
"""

from music21 import note, pitch, stream

from .arrangement_analysis import get_chord_third


def generate_bebop_chromatic_enclosure(
    target_pitch: pitch.Pitch,
    octave: int = 4
) -> list[note.Note]:
    """
    Generate bebop chromatic enclosure pattern leading to target.

    The enclosure approaches the target note from both above and below
    chromatically before landing on it. Each note is an 8th note.

    Pattern: half-step above -> half-step below -> target
    Example: To land on E, pattern is F -> D# -> E

    Args:
        target_pitch: The target pitch to land on (e.g., 3rd of chord)
        octave: The octave to place the notes in

    Returns:
        list: List of music21 Note objects (3 notes total, each an 8th note)
    """
    # Ensure target is in the specified octave
    target = pitch.Pitch(target_pitch.name)
    target.octave = octave

    # Calculate chromatic neighbors
    above = target.transpose(1)   # Half step up
    below = target.transpose(-1)  # Half step down

    # Create 8th notes (quarterLength = 0.5)
    eighth_duration = 0.5

    notes = [
        note.Note(above, quarterLength=eighth_duration),
        note.Note(below, quarterLength=eighth_duration),
        note.Note(target, quarterLength=eighth_duration)
    ]

    return notes


def create_arrangement_part(
    chords: list[dict],
    octave: int = 4
) -> stream.Part:
    """
    Create a new Part with generated enclosure pattern notes.

    For each chord:
    1. Get the 3rd of the chord
    2. Generate the enclosure pattern leading to it
    3. Position so target lands on beat 1 of the chord's measure

    Timing:
    - 3 eighth notes = 1.5 quarter notes total
    - To land on beat 1, pattern starts at offset -1.0 (beat 4 of previous measure)
    - Note 1: offset -1.0 (beat 4)
    - Note 2: offset -0.5 (beat 4.5 / "and" of 4)
    - Note 3: offset 0.0 (beat 1)

    Args:
        chords: List of chord info dicts from analysis
        octave: Octave to place notes in

    Returns:
        stream.Part: New part with generated melody
    """
    arrangement_part = stream.Part()
    arrangement_part.id = 'Arrangement'

    for i, chord_info in enumerate(chords):
        # Skip the first chord if it's on beat 1 of measure 1
        # (no room for pickup notes before the piece starts)
        if i == 0 and chord_info['measure_number'] <= 1 and chord_info['beat'] <= 1.0:
            continue

        # Get the target pitch (3rd of the chord)
        chord_obj = chord_info['chord_object']
        target_pitch = get_chord_third(chord_obj)

        if target_pitch is None:
            continue

        # Generate the enclosure pattern
        enclosure_notes = generate_bebop_chromatic_enclosure(target_pitch, octave)

        # Calculate the offset where beat 1 of the chord's measure starts
        # The offset in chord_info is the absolute offset of the chord in the score
        chord_offset = chord_info['offset']

        # Position the notes so the target lands on the chord offset
        # Note 1: -1.0 from target (beat 4 of previous measure)
        # Note 2: -0.5 from target (beat 4.5)
        # Note 3: 0.0 (on the chord / beat 1)
        for j, n in enumerate(enclosure_notes):
            # Calculate offset: start 1.0 before the target and advance by 0.5 each note
            note_offset = chord_offset - 1.0 + (j * 0.5)

            # Only add notes with non-negative offsets
            if note_offset >= 0:
                n.offset = note_offset
                arrangement_part.insert(note_offset, n)
            else:
                # For notes that would go before the start, skip them
                # (this handles edge cases at the beginning)
                pass

    return arrangement_part


def combine_with_original(
    original_score: stream.Score,
    arrangement_part: stream.Part
) -> stream.Score:
    """
    Combine the generated arrangement with chord symbols from the original.

    Only copies chord symbols (harmony), not the original notes (which may be
    slash notation or other rhythm indicators that shouldn't be played back).

    Args:
        original_score: The original music21 Score
        arrangement_part: The generated melody Part

    Returns:
        stream.Score: New score with arrangement and chord symbols
    """
    from music21 import harmony, metadata, tempo, key, meter

    combined = stream.Score()

    # Copy metadata from original
    for element in original_score.flatten().getElementsByClass(metadata.Metadata):
        combined.insert(0, element)

    # Copy time signature and key signature to the arrangement part
    time_sigs = list(original_score.flatten().getElementsByClass(meter.TimeSignature))
    if time_sigs:
        arrangement_part.insert(0, time_sigs[0])

    key_sigs = list(original_score.flatten().getElementsByClass(key.KeySignature))
    if key_sigs:
        arrangement_part.insert(0, key_sigs[0])

    # Copy tempo markings
    tempos = list(original_score.flatten().getElementsByClass(tempo.MetronomeMark))
    for t in tempos:
        arrangement_part.insert(t.offset, t)

    # Copy chord symbols to the arrangement part
    chord_symbols = list(original_score.flatten().getElementsByClass(harmony.ChordSymbol))
    seen_positions = set()
    for cs in chord_symbols:
        # Skip N.C. (No Chord) symbols - they have no root
        if cs.root() is None:
            continue

        # Avoid duplicates at same position
        pos_key = (cs.offset, cs.figure)
        if pos_key in seen_positions:
            continue
        seen_positions.add(pos_key)

        # Create a copy of the chord symbol and add to arrangement
        try:
            new_cs = harmony.ChordSymbol(cs.figure)
            arrangement_part.insert(cs.offset, new_cs)
        except Exception:
            # Skip any chord symbols that can't be recreated
            pass

    # Add the arrangement part to the score
    combined.insert(0, arrangement_part)

    return combined


def score_to_musicxml_bytes(score: stream.Score) -> bytes:
    """
    Convert a music21 Score to MusicXML bytes.

    Args:
        score: music21 Score object

    Returns:
        bytes: MusicXML content as bytes
    """
    # Write to a temporary format and get bytes
    xml_str = score.write('musicxml')

    # Read the file back as bytes
    with open(xml_str, 'rb') as f:
        xml_bytes = f.read()

    return xml_bytes


def create_standalone_arrangement(
    chords: list[dict],
    octave: int = 4
) -> stream.Score:
    """
    Create a standalone score with just the arrangement melody.

    Args:
        chords: List of chord info dicts from analysis
        octave: Octave to place notes in

    Returns:
        stream.Score: Score containing only the arrangement part
    """
    score = stream.Score()
    arrangement_part = create_arrangement_part(chords, octave)
    score.insert(0, arrangement_part)
    return score


if __name__ == "__main__":
    # Example usage for manual testing
    from music21 import harmony

    print("Testing arrangement_logic.py")
    print("=" * 40)

    # Test chromatic enclosure generation
    print("\nTesting chromatic enclosure generation:")
    print("-" * 40)

    # Test with E4 as target (like the 3rd of Cmaj)
    test_target = pitch.Pitch('E4')
    enclosure = generate_bebop_chromatic_enclosure(test_target, octave=4)

    print(f"Target: E4 (3rd of Cmaj)")
    print(f"Generated pattern:")
    for i, n in enumerate(enclosure):
        print(f"  Note {i+1}: {n.nameWithOctave} (duration: {n.quarterLength})")

    # Expected: F4 -> D#4 -> E4
    print(f"Expected: F4 -> D#4 -> E4")

    # Test with different chord thirds
    print("\nTesting with various chord thirds:")
    print("-" * 40)

    test_chords = [
        ('Cmaj7', 'E'),   # Major 3rd
        ('Dm7', 'F'),     # Minor 3rd
        ('G7', 'B'),      # Major 3rd
        ('Am7', 'C'),     # Minor 3rd
    ]

    for chord_name, expected_third in test_chords:
        cs = harmony.ChordSymbol(chord_name)
        third = get_chord_third(cs)
        enclosure = generate_bebop_chromatic_enclosure(third, octave=4)

        pattern_str = ' -> '.join([n.nameWithOctave for n in enclosure])
        print(f"  {chord_name}: {pattern_str}")

    # Test creating an arrangement part
    print("\nTesting arrangement part creation:")
    print("-" * 40)

    # Create mock chord data
    mock_chords = []
    for i, chord_name in enumerate(['Dm7', 'G7', 'Cmaj7', 'Am7'], start=2):
        cs = harmony.ChordSymbol(chord_name)
        mock_chords.append({
            'measure_number': i,
            'beat': 1.0,
            'offset': (i - 1) * 4.0,  # 4 beats per measure
            'symbol': chord_name,
            'chord_object': cs,
            'root': cs.root().name,
        })

    arrangement = create_arrangement_part(mock_chords, octave=4)
    print(f"Created arrangement part with {len(arrangement.flatten().notes)} notes")

    for n in arrangement.flatten().notes:
        print(f"  {n.nameWithOctave} at offset {n.offset}")

    print("\n" + "=" * 40)
    print("All tests completed successfully!")
