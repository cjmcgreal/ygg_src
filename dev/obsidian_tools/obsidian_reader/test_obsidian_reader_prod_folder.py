#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 25 13:53:14 2025

@author: conrad
"""
from obsidian_reader import ObsidianReader
from pathlib import Path
import os

debug = False

# my example folder structure (relative)
my_dir = "/home/conrad/git/yggdrasill/prod_tree"
output_folder = ""

#%% Setup
# base_path = Path(__file__).parent      # Get the path to the current script's directory
# my_dir = str(base_path) + my_rel_dir   # full, absolute, path
# print(my_dir)

#%% Instantiate
obs_rdr = ObsidianReader(my_dir)
obs_rdr.print_path() # execute most basic function

# list all notes
all_notes = obs_rdr.list_all_notes()

if debug:
    for file in all_notes:
        print(file)

assert all_notes, "List is empty!"

#%% find notes by property


#%% folder tree builder
output_csv = 'test/temp/folder_tree.csv'
obs_rdr.generate_folder_tree_csv(output_csv)
        
#%% export parent tree
output_csv = 'test/temp/parent_tree.csv'
obs_rdr.generate_parent_tree_csv(output_csv)

#%% export prereq tree
output_csv = 'test/temp/prereq_tree.csv'
obs_rdr.generate_prereq_tree_csv(output_csv)

#%% create "driven_by" tree
output_csv = 'test/temp/driven_by_tree.csv'
obs_rdr.generate_driven_by_tree_csv(output_csv)
