#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 27 17:18:42 2025

@author: conrad
"""

import pandas as pd

CSV_PATH = "trips.csv"

# Read
df = pd.read_csv(CSV_PATH, dtype=str).fillna("")
# Coerce some types
df["distance"] = pd.to_numeric(df["distance"], errors="coerce")
df["cultural_rank"] = pd.to_numeric(df["cultural_rank"], errors="coerce")
for col in ["completed","kayak_required","paraglide_required","ski_required"]:
    df[col] = df[col].str.upper().isin(["TRUE","T","1","YES","Y"])

# Build quick lookup dicts
by_id = {row.trip_id: row for _, row in df.iterrows()}

def _chain_ready(trip_id: str, disc: str, seen=None) -> bool:
    """
    Returns True if the discipline chain for `disc` is satisfied for `trip_id`.
    Rule: If <disc>_required is False → ready for that discipline.
          If required and no predecessor → ready (base step).
          If required and predecessor exists → that predecessor must be completed,
          AND its own predecessor chain must also be satisfied (recursive).
    """
    if trip_id not in by_id:
        return False
    row = by_id[trip_id]

    required = bool(row[f"{disc}_required"])
    if not required:
        return True  # no constraint for this discipline

    prev_id = str(row.get(f"{disc}_prev_id", "")).strip()
    if prev_id == "":
        return True  # required but base step (no previous)

    # Cycle protection
    if seen is None:
        seen = set()
    if (disc, trip_id) in seen:
        # Cycle detected; not ready
        return False
    seen.add((disc, trip_id))

    # The immediate predecessor must be completed
    prev_row = by_id.get(prev_id)
    if prev_row is None:
        return False  # bad reference
    if not bool(prev_row["completed"]):
        return False

    # And its own chain must be valid too
    return _chain_ready(prev_id, disc, seen)

def feasible(trip_id: str) -> bool:
    """Trip is feasible only if all required disciplines are ready."""
    return (
        _chain_ready(trip_id, "kayak") and
        _chain_ready(trip_id, "paraglide") and
        _chain_ready(trip_id, "ski")
    )

# Compute feasibility and why_blocked
feasible_list = []
why_list = []
for tid in df["trip_id"]:
    ok_k = _chain_ready(tid, "kayak")
    ok_p = _chain_ready(tid, "paraglide")
    ok_s = _chain_ready(tid, "ski")
    ok_all = ok_k and ok_p and ok_s
    feasible_list.append(ok_all)

    reasons = []
    if not ok_k and by_id[tid]["kayak_required"]:
        prev_id = str(by_id[tid]["kayak_prev_id"]).strip()
        if prev_id and prev_id in by_id and not bool(by_id[prev_id]["completed"]):
            reasons.append(f"kayak prev {prev_id} not completed")
        else:
            reasons.append("kayak chain not satisfied")
    if not ok_p and by_id[tid]["paraglide_required"]:
        prev_id = str(by_id[tid]["paraglide_prev_id"]).strip()
        if prev_id and prev_id in by_id and not bool(by_id[prev_id]["completed"]):
            reasons.append(f"paraglide prev {prev_id} not completed")
        else:
            reasons.append("paraglide chain not satisfied")
    if not ok_s and by_id[tid]["ski_required"]:
        prev_id = str(by_id[tid]["ski_prev_id"]).strip()
        if prev_id and prev_id in by_id and not bool(by_id[prev_id]["completed"]):
            reasons.append(f"ski prev {prev_id} not completed")
        else:
            reasons.append("ski chain not satisfied")
    why_list.append("; ".join(reasons))

df["feasible"] = feasible_list
df["why_blocked"] = why_list

# Views:
ready = df[df["feasible"]].copy()
blocked = df[~df["feasible"]].copy()

# (i) Sort feasible by cultural value (rank ascending)
ready_by_culture = ready.sort_values(["cultural_rank","distance"], ascending=[True, True])

# (ii) Sort feasible by distance (ascending); tie-break by cultural rank
ready_by_distance = ready.sort_values(["distance","cultural_rank"], ascending=[True, True])

# Display in IDE (plain prints)
print("\n=== READY NOW (by cultural rank) ===")
print(ready_by_culture[["trip_id","name","country","distance","cultural_rank"]])

print("\n=== READY NOW (by distance) ===")
print(ready_by_distance[["trip_id","name","country","distance","cultural_rank"]])

print("\n=== FUTURE UNLOCKS (blocked with reasons) ===")
print(blocked[["trip_id","name","why_blocked"]].sort_values("name"))
