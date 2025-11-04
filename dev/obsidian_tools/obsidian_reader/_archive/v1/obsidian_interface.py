#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 25 12:32:55 2025

@author: conrad
"""

from vault_crawler import VaultCrawler
from tree_builder import VaultTreeBuilder
from mermaid_renderer import MermaidRenderer

vault = VaultCrawler("/Users/conrad/Obsidian/MyVault")
parsed_notes = vault.parse()

tree = VaultTreeBuilder(parsed_notes)
gantt_tree = tree.build_by_parent_fallback_folder()
flow_tree = tree.build_by_status()

mermaid = MermaidRenderer()
print(mermaid.render_gantt(gantt_tree))
print(mermaid.render_flowchart(flow_tree))