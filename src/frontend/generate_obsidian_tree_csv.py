#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, sys

# Add the parent's parent directory to sys.path, to make it possible to import obsidian reader
parent = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if parent not in sys.path:
    sys.path.insert(0, parent)

from database.obsidian_reader.obsidian_reader import ObsidianReader

def main():

    #%% prod folder
    # my_dir = "/home/conrad/git/yggdrasill/prod_tree"
    great_grandparent = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    my_dir = great_grandparent + "/prod_tree"
    output_dir = "data"
    
    obs_rdr = ObsidianReader(my_dir)
    obs_rdr.generate_all_csvs(output_dir)


if __name__ == "__main__":
    main()