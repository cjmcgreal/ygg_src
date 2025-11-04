#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul 26 15:00:05 2025

@author: conrad
"""

import frontmatter
from pathlib import Path
from typing import List

def generate_mermaid_gantt(vault_path: str, diagram_title: str = "Auto-generated Gantt Chart") -> str:
    notes = Path(vault_path).rglob("*.md")
    tasks = []

    for note_path in notes:
        post = frontmatter.load(note_path)
        fm = post.metadata

        if fm.get("diagram_type") != "gantt":
            continue

        task = {
            "id": fm.get("id"),
            "title": fm.get("title", note_path.stem),
            "start": fm.get("start"),
            "duration": fm.get("duration", "1d"),
            "depends_on": fm.get("depends_on", []),
            "section": fm.get("section", "General"),
            "status": fm.get("status", ""),
        }

        if not task["id"] or not task["start"]:
            continue  # Skip if required fields missing

        tasks.append(task)

    # Group tasks by section
    from collections import defaultdict
    sections = defaultdict(list)
    for task in tasks:
        sections[task["section"]].append(task)

    # Generate Mermaid block
    output = []
    output.append("```mermaid")
    output.append("gantt")
    output.append(f"    title {diagram_title}")
    output.append("    dateFormat  YYYY-MM-DD")
    output.append("    axisFormat  %b %d\n")

    for section, items in sections.items():
        output.append(f"    section {section}")
        for task in items:
            status = f"{task['status']}," if task['status'] else ""
            dependency = f"after {task['depends_on'][0]}" if task['depends_on'] else task["start"]
            output.append(f"    {task['title']}  : {status} {task['id']}, {dependency}, {task['duration']}")
        output.append("")  # newline between sections

    output.append("```")
    return "\n".join(output)

if __name__ == "__main__":
    vault_path = "./test"
    out = generate_mermaid_gantt(vault_path)
    