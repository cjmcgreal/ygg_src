"""
General Domain - Integration Wrapper
Cross-domain dashboard aggregating content from multiple domains
"""

import sys
import os

# Add src directory to path for imports
src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from dashboard import render_general_app

__all__ = ['render_general_app']
