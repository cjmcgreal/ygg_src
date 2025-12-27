"""
Streamlit UI for the music arrangement generator.

Provides the main interface for:
1. Uploading MusicXML files with chord symbols
2. Configuring arrangement parameters
3. Generating and downloading arrangements
"""

import streamlit as st

from . import arrangement_workflow as workflow


def initialize_session_state() -> None:
    """Initialize Streamlit session state variables."""
    if 'parsed_result' not in st.session_state:
        st.session_state.parsed_result = None
    if 'generated_xml' not in st.session_state:
        st.session_state.generated_xml = None


def render_arrangement() -> None:
    """
    Main entry point called by app.py to render the full interface.
    """
    initialize_session_state()

    st.title("Bebop Arrangement Generator")
    st.markdown("""
    Generate bebop-style chromatic enclosure patterns from your chord charts.
    Upload a MusicXML file containing chord symbols, and this tool will create
    a melody line that approaches the 3rd of each chord using chromatic enclosures.
    """)

    # Create tabs
    tab_generate, tab_history = st.tabs(["Generate", "History"])

    with tab_generate:
        render_tab_generate()

    with tab_history:
        render_tab_history()


def render_tab_generate() -> None:
    """
    Tab 1: Main generation interface.
    - File uploader for MusicXML
    - Parameter configuration
    - Generate button
    - Preview of extracted chords
    - Download button for result
    """
    # File upload section
    st.subheader("1. Upload MusicXML")
    uploaded_file = st.file_uploader(
        "Upload a MusicXML file with chord symbols",
        type=['xml', 'musicxml', 'mxl'],
        help="The file should contain ChordSymbol elements (e.g., Cmaj7, Dm7, G7)"
    )

    if uploaded_file is not None:
        # Process the uploaded file
        file_content = uploaded_file.getvalue()
        result = workflow.process_musicxml_upload(file_content)

        if result['success']:
            st.session_state.parsed_result = result
            st.success(f"Parsed successfully! Found {len(result['chords'])} chord symbols.")

            # Show score structure
            st.markdown("**Score Info:**")
            structure = result['structure']
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Measures", structure.get('num_measures', 'N/A'))
            with col2:
                st.metric("Time Signature", structure.get('time_signature', 'N/A'))
            with col3:
                st.metric("Key", structure.get('key_signature', 'N/A'))

            # Show chord preview
            st.subheader("2. Chord Preview")
            if result['chords']:
                chords_df = workflow.get_chords_as_dataframe(result['chords'])
                st.dataframe(chords_df, use_container_width=True)
            else:
                st.warning("No chord symbols found in the file. Make sure your MusicXML contains ChordSymbol elements.")

            # Configuration section
            st.subheader("3. Configure Pattern")

            col1, col2 = st.columns(2)
            with col1:
                octave = st.selectbox(
                    "Octave",
                    options=[3, 4, 5, 6],
                    index=1,  # Default to octave 4
                    help="The octave to place the generated melody notes in"
                )

            with col2:
                st.markdown("**Pattern: Bebop Chromatic Enclosure**")
                st.caption("Approaches the 3rd of each chord from a half-step above, then below")
                st.caption("Example: F -> D# -> E (to land on E, the 3rd of Cmaj)")

            # Generate button
            st.subheader("4. Generate")

            if len(result['chords']) > 0:
                if st.button("Generate Arrangement", type="primary"):
                    with st.spinner("Generating arrangement..."):
                        gen_result = workflow.generate_arrangement(
                            chords=result['chords'],
                            original_score=result['score'],
                            octave=octave,
                            input_filename=uploaded_file.name
                        )

                    if gen_result['success']:
                        st.session_state.generated_xml = gen_result['output_xml']
                        st.success(f"Generated {gen_result['num_notes']} notes!")
                    else:
                        st.error(f"Generation failed: {gen_result['error']}")
            else:
                st.warning("No chords to generate from. Upload a file with chord symbols.")

            # Download section
            if st.session_state.generated_xml is not None:
                st.subheader("5. Download")

                # Create download filename
                original_name = uploaded_file.name.rsplit('.', 1)[0]
                download_name = f"{original_name}_arrangement.xml"

                st.download_button(
                    label="Download MusicXML",
                    data=st.session_state.generated_xml,
                    file_name=download_name,
                    mime="application/vnd.recordare.musicxml+xml"
                )

        else:
            st.error(f"Failed to parse file: {result['error']}")
            st.session_state.parsed_result = None


def render_tab_history() -> None:
    """Tab 2: View generation history."""
    st.subheader("Generation History")

    history = workflow.get_generation_history(20)

    if len(history) > 0:
        st.dataframe(history, use_container_width=True)
    else:
        st.info("No generation history yet. Generate an arrangement to see it here.")


if __name__ == "__main__":
    # This allows running the app directly for testing
    # Run with: streamlit run src/arrangement/arrangement_app.py
    print("Run this module with: streamlit run src/arrangement/arrangement_app.py")
    print("Or run the main app with: streamlit run app.py")
