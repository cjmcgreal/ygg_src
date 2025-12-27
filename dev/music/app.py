"""
Music Arrangement Generator

A web app for generating bebop-style arrangements from chord charts.
Upload a MusicXML file with chord symbols, configure patterns, and
download the generated arrangement.

Run with: streamlit run app.py
"""

import streamlit as st
from src.arrangement.arrangement_app import render_arrangement

st.set_page_config(
    page_title="Music Arrangement Generator",
    layout="wide"
)

render_arrangement()


if __name__ == "__main__":
    print("Run this app with: streamlit run app.py")
