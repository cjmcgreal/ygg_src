```yaml
spec_id: critical_blend_slider_v1
purpose: >
  Produce a slider that ALWAYS changes the sorted order of items by blending two metrics (distance, culture).
  Slider steps correspond to intervals between pairwise order-change breakpoints. Ends match pure sorts.

inputs:
  dataset: pandas.DataFrame
  required_columns:
    - trip_id
    - name
    - country
    - distance            # numeric
    - cultural_rank       # numeric; lower rank = higher priority; treat as "cost"
    - completed           # boolean-like
    - kayak_required      # boolean-like
    - kayak_prev_id       # string or ""
    - paraglide_required  # boolean-like
    - paraglide_prev_id   # string or ""
    - ski_required        # boolean-like
    - ski_prev_id         # string or ""
  booleans_truthy: ["TRUE","T","1","YES","Y"]

feasibility:
  model: >
    Each discipline forms a chain via *_prev_id. A trip is feasible iff for every required discipline:
    either prev_id == "" (base) OR the predecessor trip is completed AND its own chain is satisfied (recursive).
  function_signature: feasible(df) -> df_with_columns[feasible:bool, why_blocked:str]

normalization:
  goal: Make metrics comparable, lower-is-better in [0,1].
  methods:
    min_max: d_norm=(distance-min(distance))/(max(distance)-min(distance)); same for c_norm from cultural_rank
    rank: rank ascending to 1..n, then scale to [0,1] via (rank-1)/(n-1)
  selected_by: param norm_method in {"min-max","rank"}
  note: Do NOT invert cultural_rank; it is already a "cost" (smaller rank = better).

blend_model:
  parameter_t: t in [0,1]                      # continuous blend knob
  score_per_item: s_i(t)=(1-t)*d_i + t*c_i     # d_i,c_i are normalized costs
  display_weights:                              # for UI only; sum fixed at 1000
    w_cult=round(1000*t)
    w_dist=1000-w_cult

breakpoints:
  definition: >
    Order changes only when two score lines cross.
    For items i,j with (d_i,c_i) and (d_j,c_j):
    t*=(d_j-d_i)/((c_i-d_i)-(c_j-d_j)). Keep only 0<t*<1 and |denominator|>eps.
  algorithm:
    - compute all pairwise t* (i<j); O(n^2)
    - keep 0<t*<1; deduplicate with rounding; sort ascending
    - knots=[0]+breakpoints+[1]
    - steps=[0] + midpoints between successive knots + [1] (use exact 0 and 1 at ends)
  guarantee: Each step yields a distinct permutation of the ready set (piecewise-constant ordering).

sorting:
  reference_orders:
    by_distance: sort by [distance asc, cultural_rank asc, trip_id asc]
    by_culture:  sort by [cultural_rank asc, distance asc, trip_id asc]
  global_sort(t):
    if t<=eps: return by_distance
    if t>=1-eps: return by_culture
    else:
      compute s_i(t) on normalized metrics
      sort by [s_i asc, distance asc, cultural_rank asc, trip_id asc]
  eps: 1e-12

ui_contract:
  slider:
    type: discrete select_slider over integer step indices 0..(len(steps)-1)
    label: "Global Blend Step"
    mapping: step_index -> t = steps[step_index]
    live_weights: w_dist=round(1000*(1-t)); w_cult=1000-w_dist
  views:
    - Ready Now (by distance): reference_orders.by_distance over feasible set
    - Ready Now (by cultural rank): reference_orders.by_culture over feasible set
    - Global Sort: global_sort(t) over feasible set
    - Future Unlocks: infeasible set with why_blocked

functions:
  - name: coerce_booleans
    in: df
    out: df
    desc: Coerce boolean-like strings to True/False using booleans_truthy.
  - name: compute_feasible
    in: df
    out: df with [feasible, why_blocked]
    desc: Recursive chain check per discipline; collects reasons.
  - name: normalize_series
    in: (series, method)
    out: series_scaled_in_[0,1]
    desc: Min–max or rank normalization; lower is better.
  - name: compute_breakpoints
    in: (d_norm_array, c_norm_array, eps)
    out: sorted_unique_breakpoints_in_(0,1)
  - name: build_steps
    in: breakpoints
    out: steps_t_list_with_0_and_1_as_endpoints
  - name: global_sort
    in: (df_ready, t, eps)
    out: df_ready_sorted
  - name: weights_from_t
    in: t
    out: (w_dist=round(1000*(1-t)), w_cult=1000-w_dist)

pseudocode:
  - |
    df = load_csv(...)
    df = coerce_booleans(df)
    df = compute_feasible(df)
    ready = df[df.feasible].copy()
    ready["d_norm"] = normalize_series(ready.distance, norm_method)
    ready["c_norm"] = normalize_series(ready.cultural_rank, norm_method)
    bps = compute_breakpoints(ready.d_norm.values, ready.c_norm.values, eps=1e-12)
    steps = build_steps(bps)  # list of t, includes 0 and 1 at ends
    # UI: user selects step_index
    t = steps[step_index]
    (w_dist, w_cult) = weights_from_t(t)
    global_sorted = global_sort(ready, t, eps)

validation_tests:
  - name: extremes_identity
    assert: global_sort(ready,0).equals(sort_by_distance(ready)) AND global_sort(ready,1).equals(sort_by_culture(ready))
  - name: monotone

```