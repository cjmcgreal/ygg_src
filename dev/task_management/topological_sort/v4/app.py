
import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Trip Feasibility & Priority — Critical Blend", layout="wide")

st.title("Trip Feasibility & Priority — Critical Blend Slider")
st.caption("Feasible set via discipline chains. Global order changes only at computed 'critical' blend values t∈[0,1]. We map these to a discrete slider so every tick changes the order. We enforce w_dist + w_cult = 1000.")

# ---------------- Sidebar: data + options ----------------
st.sidebar.header("Controls")
uploaded = st.sidebar.file_uploader("Upload trips CSV", type=["csv"], help="If omitted, a 20-row demo loads.")
norm_method = st.sidebar.selectbox("Normalization", ["min-max", "rank"], help="Make distance & cultural comparable. Lower is better in both.")
show_debug = st.sidebar.checkbox("Show debug (breakpoints)", value=False)

# Blend slider will be built AFTER we compute critical steps.

# ---------------- Data loading ----------------
def load_df(file) -> pd.DataFrame:
    df = pd.read_csv(file, dtype=str).fillna("")
    # Cast numeric
    df["distance"] = pd.to_numeric(df["distance"], errors="coerce")
    df["cultural_rank"] = pd.to_numeric(df["cultural_rank"], errors="coerce")
    # Booleans
    for col in ["completed","kayak_required","paraglide_required","ski_required"]:
        df[col] = df[col].str.upper().isin(["TRUE","T","1","YES","Y"])
    # Ensure prev columns
    for col in ["kayak_prev_id","paraglide_prev_id","ski_prev_id"]:
        if col not in df.columns: df[col] = ""
    return df

df = load_df('trips_20.csv')

# ---------------- Feasibility ----------------
by_id = {row.trip_id: row for _, row in df.iterrows()}

def _chain_ready(trip_id: str, disc: str, seen=None) -> bool:
    if trip_id not in by_id: return False
    row = by_id[trip_id]
    required = bool(row[f"{disc}_required"])
    if not required: return True
    prev_id = str(row.get(f"{disc}_prev_id","")).strip()
    if prev_id == "": return True
    if seen is None: seen=set()
    key=(disc,trip_id)
    if key in seen: return False
    seen.add(key)
    prev = by_id.get(prev_id)
    if prev is None: return False
    if not bool(prev["completed"]): return False
    return _chain_ready(prev_id, disc, seen)

def compute_feasible(_df: pd.DataFrame) -> pd.DataFrame:
    feas, why = [], []
    for tid in _df["trip_id"]:
        ok_k = _chain_ready(tid,"kayak")
        ok_p = _chain_ready(tid,"paraglide")
        ok_s = _chain_ready(tid,"ski")
        ok = ok_k and ok_p and ok_s
        feas.append(ok)

        reasons=[]
        if not ok_k and by_id[tid]["kayak_required"]:
            pid=str(by_id[tid]["kayak_prev_id"]).strip()
            if pid and pid in by_id and not bool(by_id[pid]["completed"]):
                reasons.append(f"kayak prev {pid} not completed")
            else:
                reasons.append("kayak chain not satisfied")
        if not ok_p and by_id[tid]["paraglide_required"]:
            pid=str(by_id[tid]["paraglide_prev_id"]).strip()
            if pid and pid in by_id and not bool(by_id[pid]["completed"]):
                reasons.append(f"paraglide prev {pid} not completed")
            else:
                reasons.append("paraglide chain not satisfied")
        if not ok_s and by_id[tid]["ski_required"]:
            pid=str(by_id[tid]["ski_prev_id"]).strip()
            if pid and pid in by_id and not bool(by_id[pid]["completed"]):
                reasons.append(f"ski prev {pid} not completed")
            else:
                reasons.append("ski chain not satisfied")
        why.append("; ".join(reasons))
    out=_df.copy()
    out["feasible"]=feas
    out["why_blocked"]=why
    return out

df = compute_feasible(df)
ready = df[df["feasible"]].copy().reset_index(drop=True)
blocked = df[~df["feasible"]].copy().reset_index(drop=True)

# ---------------- Normalization ----------------
def normalize(s: pd.Series, method: str) -> pd.Series:
    # lower is better (0 best → 1 worst)
    if method == "min-max":
        mn, mx = np.nanmin(s.values), np.nanmax(s.values)
        if mx - mn < 1e-12:
            return pd.Series(np.zeros(len(s)), index=s.index)
        return (s - mn) / (mx - mn)
    elif method == "rank":
        r = s.rank(method="average", ascending=True)  # 1..n (1=best)
        return (r - 1) / (len(s) - 1) if len(s) > 1 else pd.Series(np.zeros(len(s)), index=s.index)
    else:
        return s  # fallback

ready["d_norm"] = normalize(ready["distance"], norm_method)
ready["c_norm"] = normalize(ready["cultural_rank"], norm_method)

# For reference tables (still equivalent orders)
ready_by_distance = ready.sort_values(["distance","cultural_rank"], ascending=[True,True]).reset_index(drop=True)
ready_by_culture = ready.sort_values(["cultural_rank","distance"], ascending=[True,True]).reset_index(drop=True)

# ---------------- Critical t computation ----------------
# Score_i(t) = (1-t)*d_i + t*c_i = d_i + t*(c_i - d_i)
# Find t where two items i,j swap: d_i + t*(c_i - d_i) = d_j + t*(c_j - d_j)
# => t = (d_j - d_i) / ((c_i - d_i) - (c_j - d_j))

def critical_ts(d: np.ndarray, c: np.ndarray):
    n = len(d)
    ts = []
    pairs = []
    eps=1e-12
    for i in range(n):
        for j in range(i+1, n):
            den = (c[i]-d[i]) - (c[j]-d[j])
            if abs(den) < eps:
                continue  # parallel lines: never cross within finite t (or identical)
            t = (d[j]-d[i]) / den
            if t > 0.0 + 1e-12 and t < 1.0 - 1e-12:
                ts.append(t)
                pairs.append((i,j,t))
    # unique & sorted
    if not ts:
        uniq = []
    else:
        uniq = sorted(set([round(float(t),12) for t in ts]))
    # knots include 0 and 1
    knots = [0.0] + uniq + [1.0]
    # midpoints for intervals; force exact endpoints for extremes to guarantee identity
    mids = [0.0]
    for k in range(len(knots)-1):
        left, right = knots[k], knots[k+1]
        if k == len(knots)-2:
            mids.append(1.0)  # last interval uses 1.0 exactly
        else:
            mids.append( (left + right)/2.0 )
    # Build a little table for debugging
    bp_table = pd.DataFrame({"t": uniq})
    return uniq, knots, mids, bp_table, pairs

uniq, knots, mids, bp_table, pairs = critical_ts(ready["d_norm"].to_numpy(), ready["c_norm"].to_numpy())

# ---------------- Build discrete slider over intervals ----------------
steps = list(range(len(mids)))
labels = []
for idx, t in enumerate(mids):
    wd = int(round(1000*(1.0 - t)))
    wc = 1000 - wd
    labels.append(f"step {idx} — t={t:.4f} → wd={wd}, wc={wc}")

# We use select_slider to ensure discrete steps; every tick changes the order deterministically.
choice = st.select_slider("Global Blend Step (each step changes order)",
                          options=steps,
                          value=0,
                          format_func=lambda i: labels[i])

t = float(mids[choice])
w_dist = int(round(1000*(1.0 - t)))
w_cult = 1000 - w_dist

st.write(f"**Active weights** → w_dist = {w_dist}, w_cult = {w_cult}  (t={t:.4f}, sum=1000)")

def global_sorted_by_t(ready_df: pd.DataFrame, t: float) -> pd.DataFrame:
    tmp = ready_df.copy()
    # Weighted sum on normalized values (lower is better)
    tmp["global_score"] = (1.0 - t)*tmp["d_norm"] + t*tmp["c_norm"]
    # Extremes: return exact reference orders
    eps=1e-12
    if t <= eps: return ready_by_distance.copy()
    if t >= 1.0 - eps: return ready_by_culture.copy()
    return tmp.sort_values(["global_score","distance","cultural_rank"], ascending=[True,True,True]).reset_index(drop=True)

global_sorted = global_sorted_by_t(ready, t)

# ---------------- Layout ----------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("Ready Now (by distance)")
    #st.dataframe(ready_by_distance[["trip_id","name","country","distance","cultural_rank"]], use_container_width=True)
with col2:
    st.subheader("Ready Now (by cultural rank)")
    #st.dataframe(ready_by_culture[["trip_id","name","country","distance","cultural_rank"]], use_container_width=True)

st.subheader("Global Sort (critical-blend step)")
st.caption("Score = (1−t)·d_norm + t·c_norm, with t chosen from interval midpoints between all pairwise breakpoints. Every tick changes the order.")
st.dataframe(global_sorted[["trip_id","name","country","distance","cultural_rank"]], use_container_width=True)

st.subheader("Future Unlocks (blocked with reasons)")
st.dataframe(blocked[["trip_id","name","country","why_blocked","distance","cultural_rank"]].sort_values("name").reset_index(drop=True),
             use_container_width=True)

if show_debug:
    st.markdown("### Debug: Breakpoints")
    if len(uniq)==0:
        st.info("No internal breakpoints — order never changes between pure distance (t=0) and pure culture (t=1).")
    else:
        st.write("Unique interior breakpoints t (where the order can flip):")
        st.dataframe(bp_table, use_container_width=True)
        st.write("Number of steps (including extremes):", len(mids))
