#!/bin/bash
cd "$(dirname "$0")"

# Exit on error
set -e

# Define load folder 1
vault_path=""
template_folder_path=""

# Python script creates the csv based on obsidian
load_file="generate_obsidian_tree_csv.py" # prod
# load_file="load_obsidian_tree_by_folder_v2.py" # for messing around

echo "Running $load_file"
python3 $load_file $vault_path $template_folder_path

# Step 2: Launch Streamlit app
echo "Launching Streamlit app..."
streamlit run app.py --server.address=0.0.0.0
