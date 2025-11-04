#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  6 15:30:14 2025

@author: conrad
"""

import sys
import os
import pytest

def main():
    # example: test folders to run
    include_dirs = ["domains/exercise"]
    
    # example: test folders or files to ignore
    ignore_dirs = ["domains/exercise/archive"]
    
    # build pytest args
    pytest_args = []
    
    # add include dirs
    pytest_args.extend(include_dirs)
    
    # add ignore patterns
    for ignore in ignore_dirs:
        pytest_args.extend(["--ignore", ignore])

    # optiona; show detailed output
    pytest_args.append("-v")
    
    # run tests with arguments
    retcode = sys.exit(pytest.main(pytest_args))
    
    return retcode
    
if __name__ == "__main__":
    sys.path.insert(0,os.path.abspath(os.path.dirname(__file__)))
    retcode = main()
    # retcode = sys.exit(pytest.main(["tests"]))