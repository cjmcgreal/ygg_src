"""
Exercise App - Integration wrapper for prod environment

This file acts as the integration point between the prod app structure
and the existing exercise module from the dev folder.
"""
import sys
import os

# Add the domains/exercise directory to Python path so modules can import each other
exercise_dir = os.path.dirname(os.path.abspath(__file__))
if exercise_dir not in sys.path:
    sys.path.insert(0, exercise_dir)

# Import the main render function from the src subfolder
from src.exercise_app import render_exercise_app

# Export the render function for use by the main app.py
__all__ = ['render_exercise_app']


if __name__ == "__main__":
    # Standalone test
    print("Exercise App - Integration Wrapper")
    print("=" * 50)
    print("This wrapper integrates the exercise module into the prod environment")
    print("Run the main app.py to see the full integrated UI")
    print("\nTo test: streamlit run ../../app.py")
