"""
Simple Flask server for Pragmatic Drag and Drop demo.

Serves the HTML frontend and provides API endpoints
to read/write item data from a CSV file.

Usage:
    python server.py

Then open http://localhost:5000 in your browser.
"""

import os
import pandas as pd
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS

# ========================================
# CONFIGURATION
# ========================================

# Path to the CSV data file
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
CSV_PATH = os.path.join(DATA_DIR, 'items.csv')

# Create Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for local development


# ========================================
# DATABASE FUNCTIONS (CSV Operations)
# ========================================

def load_items():
    """
    Load all items from the CSV file.

    Returns:
        pd.DataFrame: DataFrame containing all items
    """
    if not os.path.exists(CSV_PATH):
        # Create empty DataFrame with expected columns if file doesn't exist
        return pd.DataFrame(columns=['id', 'name', 'type', 'parent', 'status'])

    df = pd.read_csv(CSV_PATH)
    # Replace NaN with empty string for parent column
    df['parent'] = df['parent'].fillna('')
    return df


def save_items(df):
    """
    Save items DataFrame to the CSV file.

    Args:
        df (pd.DataFrame): DataFrame containing all items
    """
    # Ensure data directory exists
    os.makedirs(DATA_DIR, exist_ok=True)
    df.to_csv(CSV_PATH, index=False)


def update_item(item_id, updates):
    """
    Update a single item in the CSV.

    Args:
        item_id (str): The ID of the item to update
        updates (dict): Dictionary of field:value pairs to update

    Returns:
        dict: The updated item, or None if not found
    """
    df = load_items()

    # Find the item by ID
    mask = df['id'] == item_id
    if not mask.any():
        return None

    # Apply updates
    for field, value in updates.items():
        if field in df.columns:
            df.loc[mask, field] = value

    # Save back to CSV
    save_items(df)

    # Return the updated item
    updated_row = df[mask].iloc[0].to_dict()
    return updated_row


# ========================================
# API ROUTES
# ========================================

@app.route('/')
def serve_index():
    """Serve the main HTML page."""
    return send_file('index.html')


@app.route('/api/items', methods=['GET'])
def get_items():
    """
    Get all items from the CSV.

    Returns:
        JSON array of all items
    """
    df = load_items()
    items = df.to_dict(orient='records')
    return jsonify(items)


@app.route('/api/items/<item_id>', methods=['PUT'])
def update_item_route(item_id):
    """
    Update a single item.

    Expects JSON body with fields to update, e.g.:
        {"status": "done"}
        {"parent": "documents"}

    Args:
        item_id: The ID of the item to update

    Returns:
        JSON object of the updated item
    """
    updates = request.get_json()

    if not updates:
        return jsonify({'error': 'No update data provided'}), 400

    updated_item = update_item(item_id, updates)

    if updated_item is None:
        return jsonify({'error': f'Item {item_id} not found'}), 404

    return jsonify(updated_item)


@app.route('/api/items/<item_id>/parent', methods=['PUT'])
def update_item_parent(item_id):
    """
    Update an item's parent (used by Tree view).

    Expects JSON body: {"parent": "new_parent_id"}
    Use empty string "" for root level.

    Args:
        item_id: The ID of the item to update

    Returns:
        JSON object of the updated item
    """
    data = request.get_json()
    new_parent = data.get('parent', '')

    updated_item = update_item(item_id, {'parent': new_parent})

    if updated_item is None:
        return jsonify({'error': f'Item {item_id} not found'}), 404

    return jsonify(updated_item)


@app.route('/api/items/<item_id>/status', methods=['PUT'])
def update_item_status(item_id):
    """
    Update an item's status (used by Board view).

    Expects JSON body: {"status": "todo|in-progress|done"}

    Args:
        item_id: The ID of the item to update

    Returns:
        JSON object of the updated item
    """
    data = request.get_json()
    new_status = data.get('status')

    if new_status not in ['todo', 'in-progress', 'done']:
        return jsonify({'error': 'Invalid status. Must be: todo, in-progress, done'}), 400

    updated_item = update_item(item_id, {'status': new_status})

    if updated_item is None:
        return jsonify({'error': f'Item {item_id} not found'}), 404

    return jsonify(updated_item)


# ========================================
# MAIN ENTRY POINT
# ========================================

if __name__ == '__main__':
    print("=" * 50)
    print("Pragmatic Drag and Drop Demo Server")
    print("=" * 50)
    print(f"CSV data file: {CSV_PATH}")
    print(f"Open http://localhost:5000 in your browser")
    print("=" * 50)

    # Run the Flask development server
    app.run(debug=True, port=5000)
