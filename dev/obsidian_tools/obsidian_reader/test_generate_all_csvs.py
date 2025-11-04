#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug  4 10:27:22 2025

@author: conrad
"""

from obsidian_reader import ObsidianReader

#%% example folder
my_dir = "/home/conrad/git/yggdrasill/_src/database/obsidian_reader/test/load_obsidian_tree/example_obsidian_folder_structure"
output_dir = "/home/conrad/git/yggdrasill/_src/database/obsidian_reader/test/temp/example"

obs_rdr = ObsidianReader(my_dir)
obs_rdr.generate_all_csvs(output_dir)

#%% prod folder
my_dir = "/home/conrad/git/yggdrasill/prod_tree"
output_dir = "/home/conrad/git/yggdrasill/_src/database/obsidian_reader/test/temp"

obs_rdr = ObsidianReader(my_dir)
obs_rdr.generate_all_csvs(output_dir)