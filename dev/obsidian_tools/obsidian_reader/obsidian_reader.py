#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 25 13:53:14 2025

@author: conrad
"""

import os
import frontmatter
from pathlib import Path
import csv
import re

class ObsidianReader:
    def __init__(self, vault_path):
        self.vault_path = os.path.abspath(vault_path)
        # self.vault_path = vault_path
        
    def print_path(self):
        print(self.vault_path)
        
    def list_all_notes(self):
        vp = Path(self.vault_path)
        search_str = "*.md"
        return list(vp.rglob(search_str))
    
    def find_notes_by_property(self, property_name, target_value):
    
        vault_path = self.vault_path
        matching_notes = []

        for root, _, files in os.walk(vault_path):
            for file in files:
                if not file.endswith(".md"):
                    continue
    
                file_path = os.path.join(root, file)
    
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        post = frontmatter.load(f)
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
                    continue
    
                if post.metadata.get(property_name) == target_value:
                    matching_notes.append({
                        "path": file_path,
                        "filename": os.path.splitext(file)[0],
                        "metadata": post.metadata,
                        "content": post.content.strip()
                    })
    
        return matching_notes
    
    def update_frontmatter_property(self, file_list, key, value):
        """
        Modifies a single frontmatter property in-place,
        preserving the rest of the file content.
    
        Args:
            file_list (list): List of dicts, each with a "path" to a .md file
            key (str): Frontmatter key to update
            value (Any): Value to assign to that key
        """
        for file_dict in file_list:
            path = file_dict.get("path")
            if not path or not path.endswith(".md"):
                print(f"Skipping invalid or non-markdown path: {path}")
                continue
    
            try:
                with open(path, "r", encoding="utf-8") as f:
                    post = frontmatter.load(f)
    
                # Only change the specified frontmatter property
                original = post.metadata.get(key)
                post.metadata[key] = value
    
                with open(path, "w", encoding="utf-8") as f:
                    f.write(frontmatter.dumps(post))
    
                print(f"Updated '{key}': '{original}' → '{value}' in {path}")
            except Exception as e:
                print(f"Failed to update {path}: {e}")
            
    def generate_parent_tree_csv(self, output_csv='parent_tree.csv'):
        vault_path = self.vault_path    

        rows = []
        for root, _, files in os.walk(vault_path):
            for file in files:
                if not file.endswith(".md"):
                    continue
    
                full_path = os.path.join(root, file)
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        post = frontmatter.load(f)
                except Exception as e:
                    print(f"Error reading {file}: {e}")
                    continue
    
                parent = post.metadata.get("parent")
                if parent:
                    name = os.path.splitext(file)[0]
                    rows.append({"name": name, "parent": parent})
    
        # Step 2: Clean the rows object, to make it compatible with the tree reader
            # Cleaning logic
        name_set = set(row["name"] for row in rows)
        parent_set = set(row["parent"] for row in rows)
        
            # Add row for each parent that doesn't already exist as a name
        for missing_parent in parent_set - name_set:
            rows.append({"name": missing_parent, "parent": "root"})
        
            # Add the required second row: "root" with no parent
        rows.insert(0, {"name": "root", "parent": ""})
    
        # Step 3: Write to csv
        rows.sort(key=lambda row: row["name"].lower()) # Sort alphabetically by 'name' key
        with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=["name", "parent"])
            writer.writeheader()
            writer.writerows(rows)
    
        print(f"✅ Exported {len(rows)} rows to {output_csv}")
        
    def generate_prereq_tree_csv(self, output_csv='prereq_tree.csv'):
        vault_path = self.vault_path    
        
        rows = []
        for root, _, files in os.walk(vault_path):
            for file in files:
                if not file.endswith(".md"):
                    continue
        
                full_path = os.path.join(root, file)
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        post = frontmatter.load(f)
                except Exception as e:
                    print(f"Error reading {file}: {e}")
                    continue
        
                # skip "done" notes
                status = post.metadata.get("status")
                if status and status.lower() == "done":
                    continue
        
                parent = post.metadata.get("prerequisite")
                if parent:
                    name = os.path.splitext(file)[0]
                    rows.append({"name": name, "parent": parent})
                else:
                    name = os.path.splitext(file)[0]
                    rows.append({"name": name, "parent": "root"})
                    
        # Step 2: Clean the rows object, to make it compatible with the tree reader
            # Cleaning logic
        name_set = set(row["name"] for row in rows)
        parent_set = set(row["parent"] for row in rows)
        
            # Add row for each parent that doesn't already exist as a name
        for missing_parent in parent_set - name_set:
            if missing_parent == "root":
                pass
            else:
                rows.append({"name": missing_parent, "parent": "root"})
        
            # Add the required second row: "root" with no parent
        rows.insert(0, {"name": "root", "parent": ""})
        
        # Step 3: Write to csv
        with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=["name", "parent"])
            writer.writeheader()
            writer.writerows(rows)
        
        print(f"✅ Exported {len(rows)} rows to {output_csv}")

    def generate_driven_by_tree_csv(self, output_csv='driven_by_tree.csv'):
        vault_path = self.vault_path    

        rows = []
        for root, _, files in os.walk(vault_path):
            for file in files:
                if not file.endswith(".md"):
                    continue
    
                full_path = os.path.join(root, file)
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        post = frontmatter.load(f)
                except Exception as e:
                    print(f"Error reading {file}: {e}")
                    continue
    
                parent = post.metadata.get("driven_by")
                if parent:
                    name = os.path.splitext(file)[0]
                    rows.append({"name": name, "parent": parent})
    
        # Step 2: Clean the rows object, to make it compatible with the tree reader
            # Cleaning logic
        name_set = set(row["name"] for row in rows)
        parent_set = set(row["parent"] for row in rows)
        
            # Add row for each parent that doesn't already exist as a name
        for missing_parent in parent_set - name_set:
            rows.append({"name": missing_parent, "parent": "root"})
        
            # Add the required second row: "root" with no parent
        rows.insert(0, {"name": "root", "parent": ""})
    
        # Step 3: Write to csv
        rows.sort(key=lambda row: row["name"].lower()) # Sort alphabetically by 'name' key
        with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=["name", "parent"])
            writer.writeheader()
            writer.writerows(rows)
    
        print(f"✅ Exported {len(rows)} rows to {output_csv}")

    def generate_folder_tree_csv(self,output_filename='folder_tree.csv'):
        vault_path = Path(self.vault_path)
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
    
        with open(output_filename, "w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            for row in output_rows:
                writer.writerow(row)
    
        print(f"✅ Wrote {len(output_rows)} rows to {output_filename}")
        
    def generate_all_csvs(self,output_dir):
        my_dir = output_dir + '/folder_tree.csv'
        self.generate_folder_tree_csv(my_dir)
        
        my_dir = output_dir + '/parent_tree.csv'
        self.generate_parent_tree_csv(my_dir)
        
        my_dir = output_dir + '/prereq_tree.csv'
        self.generate_prereq_tree_csv(my_dir)
        
        my_dir = output_dir + '/driven_by_tree.csv'
        self.generate_driven_by_tree_csv(my_dir)
                