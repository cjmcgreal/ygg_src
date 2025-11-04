#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  6 10:52:10 2025

@author: conrad
"""
from domains.exercise.exercise import Exercise

class AppManager:
    def __init__(self):
        self.exercise = Exercise()
        
        
#%% 
if __name__ == '__main__':
   am = AppManager()
   am.exercise.planner.dummy()