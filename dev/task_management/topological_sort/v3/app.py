
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Trip Feasibility & Priority", layout="wide")

st.title("Trip Feasibility & Priority — Multidiscipline Constraints")
st.caption("Feasible set is determined by discipline chains (kayaking, paragliding, skiing). Global sort blends distance and cultural rank with a single blend slider where w_dist + w_cult = 1000.")

# ---------- Sidebar: Data input & blend ----------
st.sidebar.header("Controls")
uploaded = st.sidebar.file_uploader("Upload trips CSV", type=["csv"], help="Use the provided schema. If omitted, a 20-row demo loads.")

blend = st.sidebar.slider(
    "Blend weight for Cultural Rank (0 → distance, 1000 → culture)",
    min_value=0, max_value=1000, value=500, step=1
)
w_cult = float(blend)
w_dist = float(1000 - blend)
st.sidebar.write(f"w_dist = {w_dist:.0f},  w_cult = {w_cult:.0f}  (sum = {w_dist + w_cult:.0f})")

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

# Fallback demo data (20 rows)
df = load_df('trips_20.csv')

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

# ---------- Global sort (sum weights = 1000) ----------
def global_sorted(ready_df: pd.DataFrame, wd: float, wc: float) -> pd.DataFrame:
    """
    Score = wd * distance + wc * cultural_rank
    Extremes:
      - wd=1000, wc=0 -> identical to Ready-by-distance
      - wd=0, wc=1000 -> identical to Ready-by-cultural
    """
    tmp = ready_df.copy()
    tmp["global_score"] = wd * tmp["distance"] + wc * tmp["cultural_rank"]

    # Extreme-identity behavior
    eps = 1e-9
    if abs(wd - 1000.0) < eps and abs(wc - 0.0) < eps:
        return ready_by_distance.copy()
    if abs(wc - 1000.0) < eps and abs(wd - 0.0) < eps:
        return ready_by_culture.copy()

    # Normal blended ordering (lower score is better)
    return tmp.sort_values(["global_score","distance","cultural_rank"], ascending=[True, True, True]).reset_index(drop=True)

global_sorted_df = global_sorted(ready, w_dist, w_cult)

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

st.subheader("Global Sort (weighted by blend)")
st.caption("Score = (w_dist × distance)  +  (w_cult × cultural_rank). We enforce w_dist + w_cult = 1000 via the blend slider.")
st.dataframe(global_sorted_df[["trip_id","name","country","distance","cultural_rank"]], use_container_width=True)

# Validation tips
with st.expander("Validation tips"):
    st.write("- Set blend = 0   → w_dist=1000, w_cult=0 → Global Sort matches 'Ready Now (by distance)'.")
    st.write("- Set blend = 1000 → w_dist=0,   w_cult=1000 → Global Sort matches 'Ready Now (by cultural rank)'.")
    st.write("- Intermediate values produce a deterministic blended order via the weighted sum.")
