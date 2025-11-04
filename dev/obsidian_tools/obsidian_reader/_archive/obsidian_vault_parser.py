#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 16 16:24:24 2025

@author: conrad
"""

import frontmatter
import csv
from pathlib import Path
import re

vault_path = Path("/home/conrad/git/yggdrasill/yggdrasill/app/obsidian_reader/_src/test/example_obsidian_folder_structure")
output_rows = []

for md_file in vault_path.rglob("*.md"):
    print(md_file)
    try:
        post = frontmatter.load(md_file)
    except Exception as e:
        print(f"Skipping {md_file}: {e}")
        continue

    # Combine frontmatter + inline
    meta = post.metadata

    # Parse inline properties
    inline = dict(re.findall(r"(\w+)::\s*(.+)", post.content))

    # Combine
    all_props = {**meta, **inline}
    all_props["__filename"] = md_file.stem

    # Example filter: only notes with type = "feature" and status = "in-progress"
    # if all_props.get("type") == "feature" and all_props.get("status") == "in-progress":
    #     output_rows.append(all_props)
        
    output_rows.append(all_props)


# Decide which fields you want in the CSV
fieldnames = ["__filename", "parent"]

# Write CSV
with open("obsreader_out.csv", "w", newline="") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    for row in output_rows:
        writer.writerow(row)
