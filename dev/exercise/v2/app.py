"""
Main entry point for Exercise Tracker Streamlit application
"""

import streamlit as st

st.set_page_config(
    page_title="Exercise Tracker",
    page_icon="💪",
    layout="wide"
)

st.title("💪 Exercise Tracker")
st.write("Welcome to your personal workout tracking and progression system!")

st.markdown("""
## Getting Started

Navigate to the pages in the sidebar to:

1. **Exercise Library** - Create and manage exercises
2. **Create Workout** - Build workout templates
3. **Workout Overview** - Select and start workouts
4. **Workout Execution** - Track your workout in real-time
5. **History** - Review past workouts and progress
6. **Log Old Workout** - Manually enter workouts from the past

## Features

- Intelligent progression logic (rep range and linear weight schemes)
- Automatic warmup set generation
- 1RM estimation and tracking
- Comprehensive workout history
- Metadata calculation (volume, calories, etc.)
- Backfill historical workouts
""")
