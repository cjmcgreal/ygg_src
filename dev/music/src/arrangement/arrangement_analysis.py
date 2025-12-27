"""
Analysis layer for the music arrangement generator.

Contains:
- MusicXML parsing and chord extraction
- Chord position analysis
- Music structure analysis
"""

import tempfile
import os
import pandas as pd
from music21 import converter, harmony, stream, pitch


def parse_musicxml(file_content: bytes) -> stream.Score:
    """
    Parse MusicXML content into a music21 Score.

    Args:
        file_content: Raw bytes from uploaded file

    Returns:
        stream.Score: Parsed music21 Score object

    Raises:
        ValueError: If parsing fails
    """
    try:
        # music21 works best with actual files, so use a temp file
        with tempfile.NamedTemporaryFile(suffix='.musicxml', delete=False) as tmp:
            tmp.write(file_content)
            tmp_path = tmp.name

        try:
            parsed = converter.parse(tmp_path)
        finally:
            # Clean up temp file
            os.unlink(tmp_path)

        # music21 may return a Part or other stream type instead of Score
        # Wrap it in a Score if needed
        if isinstance(parsed, stream.Score):
            return parsed
        elif isinstance(parsed, stream.Part):
            score = stream.Score()
            score.insert(0, parsed)
            return score
        else:
            # Wrap whatever we got in a Score
            score = stream.Score()
            score.insert(0, parsed)
            return score
    except Exception as e:
        raise ValueError(f"Failed to parse MusicXML: {str(e)}")


def extract_chord_symbols(score: stream.Score) -> list[dict]:
    """
    Extract all chord symbols from a score with their positions.

    Args:
        score: music21 Score object

    Returns:
        list: List of chord info dicts:
            [
                {
                    'measure_number': int,
                    'beat': float,
                    'offset': float,  # absolute offset in score
                    'symbol': str,    # e.g., 'Cmaj7', 'Dm7'
                    'chord_object': harmony.ChordSymbol,
                    'root': str,      # e.g., 'C'
                    'quality': str,   # e.g., 'major', 'minor'
                }
            ]
    """
    chords = []
    seen_positions = set()  # Track (measure, beat) to avoid duplicates

    # Get all ChordSymbol objects from the flattened score
    chord_symbols = score.flatten().getElementsByClass(harmony.ChordSymbol)

    for cs in chord_symbols:
        # Get the measure containing this chord
        measure = cs.getContextByClass(stream.Measure)
        measure_number = measure.number if measure else 0

        # Calculate beat position within the measure
        beat = cs.beat if hasattr(cs, 'beat') else 1.0

        # Skip duplicates (same chord at same position, common in piano scores)
        position_key = (measure_number, beat, cs.figure)
        if position_key in seen_positions:
            continue
        seen_positions.add(position_key)

        chord_info = {
            'measure_number': measure_number,
            'beat': beat,
            'offset': cs.offset,  # absolute offset in the flattened score
            'symbol': cs.figure,  # the chord symbol string (e.g., 'Cmaj7')
            'chord_object': cs,
            'root': cs.root().name if cs.root() else 'Unknown',
            'quality': cs.quality if hasattr(cs, 'quality') else 'unknown',
        }
        chords.append(chord_info)

    return chords


def get_chord_third(chord_symbol: harmony.ChordSymbol) -> pitch.Pitch:
    """
    Get the third of a chord symbol.

    Args:
        chord_symbol: music21 ChordSymbol object

    Returns:
        pitch.Pitch: The third of the chord, or None if not available
    """
    # ChordSymbol has a .third property that returns the third
    third = chord_symbol.third
    if third is None:
        # Fallback: calculate from root + interval
        root = chord_symbol.root()
        if root is None:
            # No root means no chord (e.g., "N.C.")
            return None
        # Determine if major or minor third based on chord quality
        if 'm' in chord_symbol.figure.lower() and 'maj' not in chord_symbol.figure.lower():
            # Minor third (3 semitones)
            third = root.transpose(3)
        else:
            # Major third (4 semitones)
            third = root.transpose(4)
    return third


def get_chord_degree(chord_symbol: harmony.ChordSymbol, degree: int) -> pitch.Pitch:
    """
    Get a specific scale degree from a chord.

    Args:
        chord_symbol: music21 ChordSymbol
        degree: 1=root, 3=third, 5=fifth, 7=seventh

    Returns:
        pitch.Pitch: The requested pitch, or None if not available
    """
    if degree == 1:
        return chord_symbol.root()
    elif degree == 3:
        return get_chord_third(chord_symbol)
    elif degree == 5:
        return chord_symbol.fifth
    elif degree == 7:
        return chord_symbol.seventh
    else:
        return None


def analyze_score_structure(score: stream.Score) -> dict:
    """
    Analyze the overall structure of the score.

    Args:
        score: music21 Score object

    Returns:
        dict: {
            'time_signature': str,
            'key_signature': str,
            'num_measures': int,
            'tempo': float or None
        }
    """
    # Get time signature
    time_sigs = list(score.flatten().getElementsByClass('TimeSignature'))
    time_sig = time_sigs[0].ratioString if len(time_sigs) > 0 else '4/4'

    # Get key signature
    key_sigs = list(score.flatten().getElementsByClass('KeySignature'))
    key_sig = str(key_sigs[0]) if len(key_sigs) > 0 else 'C major'

    # Count measures - handle case where score has no parts
    num_measures = 0
    if hasattr(score, 'parts') and len(score.parts) > 0:
        measures = list(score.parts[0].getElementsByClass('Measure'))
        num_measures = len(measures)
    else:
        # Try to get measures directly from the score
        measures = list(score.flatten().getElementsByClass('Measure'))
        num_measures = len(measures)

    # Get tempo
    tempos = list(score.flatten().getElementsByClass('MetronomeMark'))
    tempo = tempos[0].number if len(tempos) > 0 else None

    return {
        'time_signature': time_sig,
        'key_signature': key_sig,
        'num_measures': num_measures,
        'tempo': tempo
    }


def chords_to_dataframe(chords: list[dict]) -> pd.DataFrame:
    """
    Convert chord list to DataFrame for display.

    Args:
        chords: List of chord info dicts

    Returns:
        pd.DataFrame: DataFrame with chord information
    """
    if not chords:
        return pd.DataFrame(columns=['Measure', 'Beat', 'Chord', 'Root'])

    df = pd.DataFrame([
        {
            'Measure': c['measure_number'],
            'Beat': c['beat'],
            'Chord': c['symbol'],
            'Root': c['root']
        }
        for c in chords
    ])
    return df


if __name__ == "__main__":
    # Example usage for manual testing
    from music21 import harmony, stream, note

    print("Testing arrangement_analysis.py")
    print("=" * 40)

    # Create a simple test score with chord symbols
    test_score = stream.Score()
    part = stream.Part()

    # Create measures with chord symbols
    for i, (chord_name, measure_num) in enumerate([
        ('Cmaj7', 1), ('Dm7', 2), ('G7', 3), ('Cmaj7', 4)
    ]):
        m = stream.Measure(number=measure_num)
        cs = harmony.ChordSymbol(chord_name)
        cs.offset = 0.0
        m.insert(0, cs)
        # Add a whole note as a placeholder
        n = note.Note('C4', quarterLength=4.0)
        m.append(n)
        part.append(m)

    test_score.insert(0, part)

    # Test chord extraction
    print("\nExtracting chord symbols...")
    chords = extract_chord_symbols(test_score)

    print(f"Found {len(chords)} chords:")
    for c in chords:
        print(f"  Measure {c['measure_number']}, Beat {c['beat']}: {c['symbol']} (root: {c['root']})")

    # Test getting chord thirds
    print("\nGetting chord thirds:")
    for c in chords:
        third = get_chord_third(c['chord_object'])
        print(f"  {c['symbol']}: third = {third}")

    # Test DataFrame conversion
    print("\nChords as DataFrame:")
    df = chords_to_dataframe(chords)
    print(df.to_string(index=False))

    # Test score structure analysis
    print("\nScore structure:")
    structure = analyze_score_structure(test_score)
    for key, value in structure.items():
        print(f"  {key}: {value}")

    print("\n" + "=" * 40)
    print("All tests completed successfully!")
