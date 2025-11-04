#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, sys

# Add the parent's parent directory to sys.path, to make it possible to import obsidian reader
parent = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if parent not in sys.path:
    sys.path.insert(0, parent)
    
grandparent = os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..','..'))
if grandparent not in sys.path:
    sys.path.insert(0, grandparent)

from database.obsidian_reader.obsidian_reader import ObsidianReader

script_dir = os.path.dirname(os.path.abspath(__file__))
# script_parent_dir = script_dir.parent


def main():

    default = "" # generates a tree-csv based on this folder
    vp1 = sys.argv[1] if len(sys.argv) > 1 else default
    vp2 = sys.argv[2] if len(sys.argv) > 2 else default
    
    vp1 = os.path.join(script_dir, "prod_tree_folder") # hack! Overwriting the arguments
    
    obs_rdr = ObsidianReader(vp1)

    data_folder_path = os.path.join(script_dir, "data/")

    output_csv = data_folder_path + "parent_tree.csv"
    obs_rdr.generate_parent_tree_csv(output_csv)


    output_csv = data_folder_path + "prereq_tree.csv"
    obs_rdr.generate_prereq_tree_csv(output_csv)


    output_csv = data_folder_path + "driven_by_tree.csv"
    obs_rdr.generate_driven_by_tree_csv(output_csv)


    obs_rdr = ObsidianReader(vp2)     # "Template tree" uses a different command line argument
    output_csv = data_folder_path + 'template_tree.csv'
    obs_rdr.generate_parent_tree_csv(output_csv)

    # Not using right this moment but might use in the future:
    # obs_rdr.generate_folder_tree_csv()


if __name__ == "__main__":
    main()