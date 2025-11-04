#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 15 21:41:03 2025

@author: conrad
"""

from data_io import DataIO

# Initialize with your Obsidian folder
folder_path = "/home/conrad/git/yggdrasill"
io = DataIO(folder_path)

# Read notes to DataFrame
df = io.read_obsidian_folder_to_df(folder_path)

#%% Export as csv
df.to_csv('obsidian_vault.csv', index=False)

#%% Write DataFrame back to Obsidian folder
export_folder = "export_prod_folder"
io.write_df_to_obsidian(df,export_folder)