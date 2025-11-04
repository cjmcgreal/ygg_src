
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Trip Feasibility & Priority", layout="wide")

st.title("Trip Feasibility & Priority — Multidiscipline Constraints")
st.caption("Feasible set is determined by discipline chains (kayaking, paragliding, skiing). Global sort interpolates between distance and cultural rank.")

# ---------- Sidebar: Data input & slider ----------
st.sidebar.header("Controls")
uploaded = st.sidebar.file_uploader("Upload trips.csv", type=["csv"], help="Use the provided schema. If omitted, demo data loads.")
weight = st.sidebar.slider(
    "Global Sort Multiplier (0 = distance, 1 = cultural rank)",
    min_value=0.0, max_value=1.0, value=0.5, step=0.01,
    help="At 0.0, Global Sort matches 'Ready Now (by distance)'. At 1.0, it matches 'Ready Now (by cultural rank)'."
)

# ---------- Load data ----------
def load_df(file) -> pd.DataFrame:
    df = pd.read_csv(file, dtype=str).fillna("")
    # types
    df["distance"] = pd.to_numeric(df["distance"], errors="coerce")
    df["cultural_rank"] = pd.to_numeric(df["cultural_rank"], errors="coerce")

    for col in ["completed","kayak_required","paraglide_required","ski_required"]:
        df[col] = df[col].str.upper().isin(["TRUE","T","1","YES","Y"])

    # Ensure prev-id columns exist (empty if missing)
    for col in ["kayak_prev_id","paraglide_prev_id","ski_prev_id"]:
        if col not in df.columns:
            df[col] = ""

    # basic checks
    required_cols = [
        "trip_id","name","country","distance","cultural_rank","completed",
        "kayak_required","kayak_prev_id","paraglide_required","paraglide_prev_id","ski_required","ski_prev_id"
    ]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        st.error(f"Missing required columns in CSV: {missing}")
    return df

# Fallback demo data
# from io import StringIO
# demo_csv = StringIO(\"\"\"trip_id,name,country,distance,cultural_rank,completed,kayak_required,kayak_prev_id,paraglide_required,paraglide_prev_id,ski_required,ski_prev_id
# T001,Local Lake Paddle,USA,15,8,TRUE,TRUE,,FALSE,,FALSE,
# T002,Intermediate River,USA,120,7,FALSE,TRUE,T001,FALSE,,FALSE,
# T003,Argentina Expedition,Argentina,6200,1,FALSE,TRUE,T002,FALSE,,FALSE,
# T004,Italy Cultural Tour,Italy,6000,2,FALSE,FALSE,,FALSE,,FALSE,
# T005,Norway Fjords,Norway,5100,3,FALSE,TRUE,T002,FALSE,,FALSE,
# T006,Frontier Ridge Hike,Chile,5800,6,FALSE,FALSE,,FALSE,,TRUE,
# T007,Glacier Approach (Ski),Chile,5900,5,FALSE,FALSE,,FALSE,,TRUE,T006
# T008,Paragliding Hills,USA,200,9,TRUE,FALSE,,TRUE,,FALSE,
# T009,High Alpine Paraglide,France,6100,4,FALSE,FALSE,,TRUE,T008,FALSE,
# \"\"\")
df = load_df('trips.csv')

# ---------- Feasibility logic ----------
by_id = {row.trip_id: row for _, row in df.iterrows()}

def _chain_ready(trip_id: str, disc: str, seen=None) -> bool:
    if trip_id not in by_id:
        return False
    row = by_id[trip_id]
    required = bool(row[f"{disc}_required"])
    if not required:
        return True
    prev_id = str(row.get(f"{disc}_prev_id", "")).strip()
    if prev_id == "":
        return True
    if seen is None:
        seen = set()
    key = (disc, trip_id)
    if key in seen:
        return False  # cycle
    seen.add(key)
    prev_row = by_id.get(prev_id)
    if prev_row is None:
        return False
    if not bool(prev_row["completed"]):
        return False
    return _chain_ready(prev_id, disc, seen)

feasible_list, why_list = [], []
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

# ---------- Ready/Blocked subsets ----------
ready = df[df["feasible"]].copy()
blocked = df[~df["feasible"]].copy()

ready_by_distance = ready.sort_values(["distance","cultural_rank"], ascending=[True, True]).reset_index(drop=True)
ready_by_culture  = ready.sort_values(["cultural_rank","distance"], ascending=[True, True]).reset_index(drop=True)

# ---------- Global sort ----------
def global_sorted(ready_df: pd.DataFrame, w: float) -> pd.DataFrame:
    # Score is a weighted sum: (1-w)*distance + w*cultural_rank
    # This guarantees: w=0 => pure distance; w=1 => pure cultural_rank
    tmp = ready_df.copy()
    tmp["global_score"] = (1.0 - w) * tmp["distance"] + w * tmp["cultural_rank"]

    # Deterministic tie-breakers shift smoothly; at extremes we show exact tables for identity.
    if w <= 0.0000001:
        print("tie breaker 1")
        return ready_by_distance.copy()
    elif w >= 0.9999999:
        print("tie breaker 2")
        return ready_by_culture.copy()
    else:
        return tmp.sort_values(["global_score","distance","cultural_rank"], ascending=[True, True, True]).reset_index(drop=True)

global_sorted_df = global_sorted(ready, weight)

# ---------- Layout ----------
col1, col2 = st.columns(2)

with col1:
    st.subheader("Ready Now (by distance)")
    st.dataframe(ready_by_distance[["trip_id","name","country","distance","cultural_rank"]], use_container_width=True)

with col2:
    st.subheader("Ready Now (by cultural rank)")
    st.dataframe(ready_by_culture[["trip_id","name","country","distance","cultural_rank"]], use_container_width=True)

st.subheader("Future Unlocks (blocked with reasons)")
st.dataframe(
    blocked[["trip_id","name","country","why_blocked","distance","cultural_rank"]].sort_values("name").reset_index(drop=True),
    use_container_width=True
)

st.subheader("Global Sort (weighted by slider)")
st.caption("Score = (1 - slider) × distance  +  (slider) × cultural_rank")
st.dataframe(global_sorted_df[["trip_id","name","country","distance","cultural_rank"]], use_container_width=True)

# Little correctness hints
with st.expander("Validation hints"):
    st.write("- Move the slider to 0.0 → Global Sort should match 'Ready Now (by distance)'.")
    st.write("- Move the slider to 1.0 → Global Sort should match 'Ready Now (by cultural rank)'.")
    st.write("- Middle values create a deterministic blended order based on the weighted sum.")
