#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug  4 08:44:30 2025

@author: conrad
"""
from pathlib import Path

vault_path = "/home/conrad/git/yggdrasill/_src/database/obsidian_reader/test/load_obsidian_tree/example_obsidian_folder_structure"
vp = Path(vault_path)
search_str = "*.md"
out = list(vp.rglob(search_str))
print(out)    