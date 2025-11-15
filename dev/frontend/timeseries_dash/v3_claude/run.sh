#!/bin/bash
# Launch script for Epic Timeseries Tool V3 - Drag & Drop Edition

echo "🚀 Launching Epic Timeseries Visualization Tool V3..."
echo ""

# Check if dependencies are installed
if ! python -c "import dash" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
fi

echo "🌐 Starting Dash server..."
python app_v2.py
