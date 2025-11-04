#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 26 10:19:18 2025

@author: conrad
"""

import csv
from pathlib import Path

def csv_to_mermaid_gitgraph(
    csv_path,
    message_col=None,      # if None, use first column
    header="gitGraph",
    preface_commits=None,  # list of strings to emit before CSV rows
    indent="   "
):
    """
    Reads a CSV and returns Mermaid gitGraph markdown where each row -> a commit.
    - message_col: name/index of the column to use for commit messages.
    - preface_commits: list of commit messages to place before the CSV-driven commits.
    """
    p = Path(csv_path)
    if not p.exists():
        raise FileNotFoundError(f"No such file: {csv_path}")

    lines = [header]
    if preface_commits:
        for m in preface_commits:
            safe = str(m).replace('"', r'\"').strip()
            if safe:
                lines.append(f'{indent}commit id: "{safe}"')

    with p.open(newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = list(reader)

    if not rows:
        return "\n".join(lines)

    # Detect header row (simple heuristic: assume first row is header if any cell is non-numeric text)
    header_row = rows[0]
    has_header = any(not c.strip().isdigit() for c in header_row)

    # Select the message column
    if message_col is None:
        # default: first column
        col_idx = 0
        col_name = header_row[0] if has_header else None
    else:
        if isinstance(message_col, int):
            col_idx = message_col
            col_name = None
        else:
            # name
            if not has_header:
                raise ValueError("message_col given as name, but CSV appears to have no header.")
            try:
                col_idx = header_row.index(message_col)
                col_name = message_col
            except ValueError:
                raise ValueError(f"Column '{message_col}' not found in CSV header: {header_row}")

    # Iterate rows (skip header if present)
    start = 1 if has_header else 0
    for r in rows[start:]:
        if col_idx >= len(r):
            continue
        msg = r[col_idx].strip()
        if not msg:
            continue
        safe = msg.replace('"', r'\"')
        lines.append(f'{indent}commit id: "{safe}"')

    return "\n".join(lines)


if __name__ == "__main__":
    # Example usage:
    # CSV example:
    #   id,author
    #   Starting State,Alice
    #   Change 1,Bob
    #   Change 2,Carol
    #   Change 3,Dave
    #   Change 4,Eve
    md = csv_to_mermaid_gitgraph(
        csv_path="example_db.csv",
        message_col="name",               # or None to use the first column
        preface_commits=None            # e.g. ["Repo init"] if you want something before rows
    )
    # Write to file (use .md or .mmd—Mermaid renderers will pick up the code fence)
    Path("gitgraph.md").write_text(f"```mermaid\n{md}\n```", encoding="utf-8")
    print("Wrote gitgraph.mmd")
