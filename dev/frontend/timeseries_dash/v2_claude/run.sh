#!/bin/bash
# Launch script for the Epic Timeseries Visualization Tool

echo "🚀 Launching the Epic Timeseries Visualization Tool..."
echo ""

# Check if streamlit is installed
if ! command -v streamlit &> /dev/null
then
    echo "❌ Streamlit not found. Installing dependencies..."
    pip install -r requirements.txt
fi

# Launch the app
streamlit run app.py
