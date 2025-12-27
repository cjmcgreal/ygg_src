"""
Workflow/orchestration layer for the arrangement generator.

Acts as the "API interface" between frontend (Streamlit) and backend layers.
Each frontend action has a dedicated function here.
"""

from music21 import stream

from . import arrangement_analysis as analysis
from . import arrangement_logic as logic
from . import arrangement_db as db


def process_musicxml_upload(file_content: bytes) -> dict:
    """
    Handle MusicXML file upload and extraction.

    Args:
        file_content: Raw bytes from uploaded file

    Returns:
        dict: {
            'success': bool,
            'score': music21.Score or None,
            'chords': list of chord info dicts,
            'structure': dict with score structure info,
            'error': str or None
        }
    """
    try:
        # Parse the MusicXML file
        score = analysis.parse_musicxml(file_content)

        # Extract chord symbols
        chords = analysis.extract_chord_symbols(score)

        # Analyze score structure
        structure = analysis.analyze_score_structure(score)

        return {
            'success': True,
            'score': score,
            'chords': chords,
            'structure': structure,
            'error': None
        }

    except ValueError as e:
        return {
            'success': False,
            'score': None,
            'chords': [],
            'structure': {},
            'error': str(e)
        }
    except Exception as e:
        return {
            'success': False,
            'score': None,
            'chords': [],
            'structure': {},
            'error': f"Unexpected error: {str(e)}"
        }


def generate_arrangement(
    chords: list[dict],
    original_score,
    octave: int = 4,
    input_filename: str = "unknown"
) -> dict:
    """
    Generate arrangement based on pattern and configuration.

    Args:
        chords: List of extracted chord info dicts
        original_score: The original music21 Score (to include chord symbols)
        octave: Octave to place the generated notes in
        input_filename: Name of the original file (for logging)

    Returns:
        dict: {
            'success': bool,
            'output_score': music21.Score,
            'output_xml': bytes (MusicXML as bytes),
            'num_notes': int,
            'error': str or None
        }
    """
    try:
        # Create the arrangement part
        arrangement_part = logic.create_arrangement_part(chords, octave)

        # Count notes generated (before combining)
        num_notes = len(arrangement_part.flatten().notes)

        # Combine with original score to keep chord symbols
        output_score = logic.combine_with_original(original_score, arrangement_part)

        # Convert to MusicXML bytes
        output_xml = logic.score_to_musicxml_bytes(output_score)

        # Log the generation
        db.log_generation(
            input_filename=input_filename,
            num_chords=len(chords),
            octave=octave
        )

        return {
            'success': True,
            'output_score': output_score,
            'output_xml': output_xml,
            'num_notes': num_notes,
            'error': None
        }

    except Exception as e:
        return {
            'success': False,
            'output_score': None,
            'output_xml': None,
            'num_notes': 0,
            'error': f"Generation error: {str(e)}"
        }


def get_chords_as_dataframe(chords: list[dict]):
    """
    Convert chord list to DataFrame for display.

    Args:
        chords: List of chord info dicts

    Returns:
        pd.DataFrame: DataFrame with chord information
    """
    return analysis.chords_to_dataframe(chords)


def get_generation_history(limit: int = 50):
    """
    Get recent generation history.

    Args:
        limit: Maximum number of records to return

    Returns:
        pd.DataFrame: Recent generation history
    """
    return db.get_recent_generations(limit)


if __name__ == "__main__":
    # Example usage for manual testing
    from music21 import harmony, stream, note

    print("Testing arrangement_workflow.py")
    print("=" * 40)

    # Create a test MusicXML-like score
    print("\nCreating test score with chord symbols...")
    test_score = stream.Score()
    part = stream.Part()

    for i, (chord_name, measure_num) in enumerate([
        ('Cmaj7', 1), ('Dm7', 2), ('G7', 3), ('Cmaj7', 4)
    ]):
        m = stream.Measure(number=measure_num)
        cs = harmony.ChordSymbol(chord_name)
        m.insert(0, cs)
        n = note.Note('C4', quarterLength=4.0)
        m.append(n)
        part.append(m)

    test_score.insert(0, part)

    # Simulate file upload by getting bytes
    print("Converting to MusicXML bytes...")
    xml_path = test_score.write('musicxml')
    with open(xml_path, 'rb') as f:
        file_bytes = f.read()

    # Test processing upload
    print("\nTesting process_musicxml_upload...")
    result = process_musicxml_upload(file_bytes)
    print(f"Success: {result['success']}")
    print(f"Chords found: {len(result['chords'])}")
    print(f"Structure: {result['structure']}")

    if result['success']:
        # Test generating arrangement
        print("\nTesting generate_arrangement...")
        gen_result = generate_arrangement(
            chords=result['chords'],
            octave=4,
            input_filename="test_song.xml"
        )
        print(f"Success: {gen_result['success']}")
        print(f"Notes generated: {gen_result['num_notes']}")

        # Show chord DataFrame
        print("\nChords as DataFrame:")
        df = get_chords_as_dataframe(result['chords'])
        print(df.to_string(index=False))

    # Show generation history
    print("\nGeneration history:")
    history = get_generation_history(5)
    if len(history) > 0:
        print(history.to_string(index=False))
    else:
        print("  (no history yet)")

    print("\n" + "=" * 40)
    print("All tests completed successfully!")
