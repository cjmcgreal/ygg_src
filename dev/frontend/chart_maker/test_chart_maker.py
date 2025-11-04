#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 28 05:28:59 2025

@author: conrad
"""
import os
from chart_maker import generate_mermaid_gantt

vault_relative_path = "./test"
vault_absolute_path = os.path.abspath(vault_relative_path)

out = generate_mermaid_gantt(vault_absolute_path)
