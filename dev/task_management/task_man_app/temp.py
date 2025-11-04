#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 15 06:30:00 2025

@author: conrad
"""

from task_man_db import load_task_data

csv_path = 'sample_tasks.csv'

df = load_task_data(csv_path)