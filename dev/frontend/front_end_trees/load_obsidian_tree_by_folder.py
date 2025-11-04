#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import frontmatter
import csv
from pathlib import Path
import re

# vault_path = Path("/home/conrad/git/yggdrasill/yggdrasill/_src/test/load_obsidian_tree/obs_ex_dir_load_tree_by_parent_prop")
vault_path = Path("/home/conrad/git/yggdrasill/Domains/Software/yggdrasill/_src/test/load_obsidian_tree/obs_ex_dir_load_tree_by_folder")
output_rows = []
debug = False

# 1. Add all folders (including subfolders)
for folder in sorted(vault_path.rglob("*")):
    if folder.is_dir():
        relative = folder.relative_to(vault_path)
        name = relative.name
        parent = relative.parent.name if relative.parent != Path('.') else None
        output_rows.append({
            "__filename": name,
            "parent": parent,
            "type": "folder"
        })

# 2. Add all markdown notes
for md_file in sorted(vault_path.rglob("*.md")):
    if debug:
        print(md_file)

    try:
        post = frontmatter.load(md_file)
    except Exception as e:
        print(f"Skipping {md_file}: {e}")
        continue

    # Get folder as parent
    relative = md_file.relative_to(vault_path)
    parent = relative.parent.name if relative.parent != Path('.') else None

    # Combine metadata + inline fields
    meta = post.metadata
    inline = dict(re.findall(r"(\w+)::\s*(.+)", post.content))
    all_props = {**meta, **inline}
    all_props["__filename"] = md_file.stem
    all_props["parent"] = parent
    all_props["type"] = "note"

    output_rows.append(all_props)

# 3. Sort and write to CSV
output_rows.sort(key=lambda row: (row.get("type", ""), row.get("__filename", "").lower()))
fieldnames = ["__filename", "parent", "type"]

with open("tree.csv", "w", newline="") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    for row in output_rows:
        writer.writerow(row)

print(f"✅ Wrote {len(output_rows)} rows to tree.csv")
