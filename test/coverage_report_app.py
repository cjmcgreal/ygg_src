#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  6 16:05:50 2025

@author: conrad
"""

import streamlit as st
from pathlib import Path

report_path = Path("domains/exercise/htmlcov/index.html")
if report_path.exists():
    st.components.v1.html(report_path.read_text(), height=800, scrolling=True)
else:
    st.warning("Test report not found.")