"""
Tests for arrangement_logic.py

Tests the core pattern generation algorithms including:
- Chromatic enclosure generation
- Arrangement part creation
"""

import pytest
from music21 import pitch, harmony

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.arrangement.arrangement_logic import (
    generate_bebop_chromatic_enclosure,
    create_arrangement_part,
)
from src.arrangement.arrangement_analysis import get_chord_third


class TestChromaticEnclosure:
    """Tests for generate_bebop_chromatic_enclosure function."""

    def test_enclosure_generates_three_notes(self):
        """Enclosure should always generate exactly 3 notes."""
        target = pitch.Pitch('E4')
        result = generate_bebop_chromatic_enclosure(target)
        assert len(result) == 3

    def test_enclosure_notes_are_eighth_notes(self):
        """Each note in the enclosure should be an 8th note (0.5 quarterLength)."""
        target = pitch.Pitch('E4')
        result = generate_bebop_chromatic_enclosure(target)
        for note in result:
            assert note.quarterLength == 0.5

    def test_enclosure_pattern_is_above_below_target(self):
        """Pattern should be: half-step above, half-step below, target."""
        target = pitch.Pitch('E4')
        result = generate_bebop_chromatic_enclosure(target, octave=4)

        # Note 1: F4 (half step above E)
        assert result[0].pitch.name == 'F'
        assert result[0].pitch.octave == 4

        # Note 2: D#4 (half step below E)
        assert result[1].pitch.name in ['D#', 'E-']  # Enharmonic equivalents
        assert result[1].pitch.octave == 4

        # Note 3: E4 (target)
        assert result[2].pitch.name == 'E'
        assert result[2].pitch.octave == 4

    def test_enclosure_respects_octave_parameter(self):
        """Notes should be placed in the specified octave."""
        target = pitch.Pitch('E')
        result = generate_bebop_chromatic_enclosure(target, octave=5)

        for note in result:
            assert note.pitch.octave == 5

    def test_enclosure_for_various_targets(self):
        """Test enclosure works for different target pitches."""
        test_cases = [
            ('C', 'C#', 'B'),   # C: above=C#, below=B
            ('G', 'G#', 'F#'),  # G: above=G#/Ab, below=F#/Gb
            ('B', 'C', 'A#'),   # B: above=C, below=A#/Bb
        ]

        for target_name, expected_above, expected_below in test_cases:
            target = pitch.Pitch(target_name + '4')
            result = generate_bebop_chromatic_enclosure(target, octave=4)

            # Check the pattern follows above-below-target
            assert result[0].pitch.midi == target.midi + 1, f"Above neighbor wrong for {target_name}"
            assert result[1].pitch.midi == target.midi - 1, f"Below neighbor wrong for {target_name}"
            assert result[2].pitch.midi == target.midi, f"Target wrong for {target_name}"


class TestArrangementPartCreation:
    """Tests for create_arrangement_part function."""

    def test_skips_first_chord_on_beat_one_measure_one(self):
        """First chord on beat 1 of measure 1 should be skipped (no room for pickup)."""
        # Create chord on measure 1, beat 1
        cs = harmony.ChordSymbol('Cmaj7')
        chords = [{
            'measure_number': 1,
            'beat': 1.0,
            'offset': 0.0,
            'symbol': 'Cmaj7',
            'chord_object': cs,
            'root': 'C',
        }]

        result = create_arrangement_part(chords)

        # Should have no notes (first chord skipped)
        assert len(result.flatten().notes) == 0

    def test_generates_notes_for_subsequent_chords(self):
        """Chords after the first should generate enclosure patterns."""
        cs1 = harmony.ChordSymbol('Cmaj7')
        cs2 = harmony.ChordSymbol('Dm7')

        chords = [
            {
                'measure_number': 1,
                'beat': 1.0,
                'offset': 0.0,
                'symbol': 'Cmaj7',
                'chord_object': cs1,
                'root': 'C',
            },
            {
                'measure_number': 2,
                'beat': 1.0,
                'offset': 4.0,  # 4 beats into the score
                'symbol': 'Dm7',
                'chord_object': cs2,
                'root': 'D',
            }
        ]

        result = create_arrangement_part(chords)

        # Should have 3 notes (enclosure for second chord only)
        assert len(result.flatten().notes) == 3


class TestChordThirdExtraction:
    """Tests for get_chord_third function."""

    def test_major_chord_third(self):
        """Major chord should have major 3rd (4 semitones from root)."""
        cs = harmony.ChordSymbol('Cmaj7')
        third = get_chord_third(cs)

        # Third of Cmaj7 is E
        assert third.name == 'E'

    def test_minor_chord_third(self):
        """Minor chord should have minor 3rd (3 semitones from root)."""
        cs = harmony.ChordSymbol('Dm7')
        third = get_chord_third(cs)

        # Third of Dm7 is F
        assert third.name == 'F'

    def test_dominant_chord_third(self):
        """Dominant 7 chord should have major 3rd."""
        cs = harmony.ChordSymbol('G7')
        third = get_chord_third(cs)

        # Third of G7 is B
        assert third.name == 'B'


if __name__ == "__main__":
    # Manual testing section
    print("Testing arrangement_logic.py")
    print("=" * 50)

    # Test 1: Chromatic enclosure generation
    print("\n1. Testing chromatic enclosure generation")
    print("-" * 50)

    target = pitch.Pitch('E4')
    enclosure = generate_bebop_chromatic_enclosure(target, octave=4)

    print(f"Target: E4 (3rd of Cmaj)")
    print(f"Generated pattern:")
    for i, n in enumerate(enclosure):
        print(f"  Note {i+1}: {n.nameWithOctave} (duration: {n.quarterLength})")
    print(f"Expected: F4 -> D#4 -> E4")

    # Verify
    assert len(enclosure) == 3, "Should generate 3 notes"
    assert all(n.quarterLength == 0.5 for n in enclosure), "All should be 8th notes"
    print("PASSED")

    # Test 2: Various chord enclosures
    print("\n2. Testing enclosures for different chords")
    print("-" * 50)

    test_chords = [
        ('Cmaj7', 'E'),
        ('Dm7', 'F'),
        ('G7', 'B'),
        ('Am7', 'C'),
        ('Fmaj7', 'A'),
    ]

    for chord_name, expected_third in test_chords:
        cs = harmony.ChordSymbol(chord_name)
        third = get_chord_third(cs)
        enclosure = generate_bebop_chromatic_enclosure(third, octave=4)

        pattern = ' -> '.join([n.nameWithOctave for n in enclosure])
        print(f"  {chord_name} (3rd={third.name}): {pattern}")

    print("PASSED")

    # Test 3: Arrangement part creation
    print("\n3. Testing arrangement part creation")
    print("-" * 50)

    # Create mock chord progression: Cmaj7 | Dm7 | G7 | Cmaj7
    mock_chords = []
    for i, chord_name in enumerate(['Cmaj7', 'Dm7', 'G7', 'Cmaj7']):
        cs = harmony.ChordSymbol(chord_name)
        mock_chords.append({
            'measure_number': i + 1,
            'beat': 1.0,
            'offset': i * 4.0,  # 4 beats per measure
            'symbol': chord_name,
            'chord_object': cs,
            'root': cs.root().name,
        })

    arrangement = create_arrangement_part(mock_chords, octave=4)
    notes = list(arrangement.flatten().notes)

    print(f"Input: 4 chords (Cmaj7 | Dm7 | G7 | Cmaj7)")
    print(f"Generated: {len(notes)} notes")
    print(f"Expected: 9 notes (3 chords x 3 notes, first chord skipped)")

    # First chord is skipped, so we should have 9 notes (3 chords * 3 notes)
    assert len(notes) == 9, f"Expected 9 notes, got {len(notes)}"

    print("\nNote offsets:")
    for n in notes:
        print(f"  {n.nameWithOctave} at offset {n.offset}")

    print("PASSED")

    # Test 4: First chord skip behavior
    print("\n4. Testing first chord skip behavior")
    print("-" * 50)

    single_chord = [{
        'measure_number': 1,
        'beat': 1.0,
        'offset': 0.0,
        'symbol': 'Cmaj7',
        'chord_object': harmony.ChordSymbol('Cmaj7'),
        'root': 'C',
    }]

    result = create_arrangement_part(single_chord)
    assert len(result.flatten().notes) == 0, "First chord on m1 beat 1 should be skipped"
    print("First chord on measure 1, beat 1 correctly skipped")
    print("PASSED")

    print("\n" + "=" * 50)
    print("All manual tests completed successfully!")
