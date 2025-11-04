#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 20 14:00:16 2025

@author: conrad
"""
# obsidian_reader features:

# Feature 3 - Bulk Edit:
    # find all notes that satisfy a particular criteria.
        # F3a - query based on property values
        # F3b - subfolder location
    # for all of those notes, change a particular property to a particular value

    # use this feature for:
        # documentation/yggdrasill/components/finance_module folders

#%% Feature 3
from obsidian_reader import ObsidianReader
my_dir = "/home/conrad/git/yggdrasill/prod_tree/test/obsidian_reader/bulk_edit/test_folder"
obs_rdr = ObsidianReader(my_dir)
all_notes = obs_rdr.list_all_notes()
for file in all_notes:
    print(file)

# find notes by property
property_name = 'property'
target_value = 'value'
found_notes = obs_rdr.find_notes_by_property(property_name, target_value)
for file in found_notes:
    print(file)

key = 'my_property'
value = 'my_value'
file_data = [{"path": file["path"]} for file in found_notes]
for file in found_notes:
    obs_rdr.update_frontmatter_property(file_data, key, value)

#%% for a list of posix paths
#  file_data = [{"path": str(p)} for p in paths]

#%% for all markdown files in a folder
from pathlib import Path

# Define your folder path (as a Path object)
my_dir = "/home/conrad/git/yggdrasill/prod_tree/test/obsidian_reader/bulk_edit/test_folder"
key = "status"
value="in-progress"

# Get all Markdown files in the folder (non-recursive)
folder_path = Path(my_dir)
note_paths = [p for p in folder_path.iterdir() if p.suffix == ".md"]

# Convert to list of dicts
file_data = [{"path": str(p)} for p in note_paths]

# Call the function
obs_rdr.update_frontmatter_property(file_data, key, value)


#%%
# Feature 1 - Read entire vault, convert to a single csv.


# Feature 2 - Export, from csv to folder structure.

        
# Feature 4 - Find all values of a particular property:
    # Find all values that the "type" property takes.

# Feature 5 - Create new note from template
# note = create_new_note_from_template(type,destination)

# Feature 6 - Find all notes in a vault where a particular property is one of: undefined, empty, "" etc

# Feature 7 - from a property contents, create an obsidian compatible link as a value of another property:
    # i.e. from "parent" create "parent_link" by adding [[ ]]


#%% Feature 4
