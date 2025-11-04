# (2) The “Trick” — Engineer Edition (you’ve seen linear algebra)

**Goal**  
Make a slider that _always_ changes the sorted order of trips by blending two metrics (distance, culture) without dead ticks.

**Setup**
- Work only on the **feasible** set (constraints already satisfied).
- Convert both metrics to **costs**: lower is better.    
- Normalize each metric so they’re comparable:
Min–max: di=Di−min⁡Dmax⁡D−min⁡Dd_i=\frac{D_i-\min D}{\max D-\min D}di​=maxD−minDDi​−minD​, ci=Ci−min⁡Cmax⁡C−min⁡Cc_i=\frac{C_i-\min C}{\max C-\min C}ci​=maxC−minCCi​−minC​
    - Or rank-normalize to [0,1] (monotone-invariant)
        

**Blend (scalarization)**
- Let t∈[0,1]t\in[0,1]t∈[0,1].
- Score line for item iii:
    si(t)=(1−t) di+t ci=di+t(ci−di)s_i(t)=(1-t)\,d_i+t\,c_i=d_i+t(c_i-d_i)si​(t)=(1−t)di​+tci​=di​+t(ci​−di​)
- Sorting by si(t)s_i(t)si​(t) gives an order that’s **piecewise constant** in ttt. The order only changes when two lines cross.
    

**Where orders flip (breakpoints)**

- Items iii and jjj swap exactly when si(t)=sj(t)s_i(t)=s_j(t)si​(t)=sj​(t):
    di+t(ci−di)=dj+t(cj−dj)⇒t\*=dj−di(ci−di)−(cj−dj)d_i+t(c_i-d_i)=d_j+t(c_j-d_j) \Rightarrow t^\*=\frac{d_j-d_i}{(c_i-d_i)-(c_j-d_j)}di​+t(ci​−di​)=dj​+t(cj​−dj​)⇒t\*=(ci​−di​)−(cj​−dj​)dj​−di​​
- Keep only t\*∈(0,1)t^\*\in(0,1)t\*∈(0,1).
- Ignore parallel lines (denominator ≈ 0).
- Deduplicate breakpoints; sort them.

**Discrete slider that always “does something”**
- Build knots: [0] + sorted breakpoints + [1][0]\,+\,\text{sorted breakpoints}\,+\,[1][0]+sorted breakpoints+[1].
    
- For each adjacent pair, take a representative ttt (midpoint).
    
- Use these ttt-values as the slider’s **only** positions.
    
- Result: every tick crosses at least one pairwise boundary → the sorted order changes.
    

**Map to your 1000-sum weights**

- Display weights, don’t drive logic:
    
    wcult=round(1000 t),wdist=1000−wcultw_{\text{cult}}=\text{round}(1000\,t),\quad w_{\text{dist}}=1000-w_{\text{cult}}wcult​=round(1000t),wdist​=1000−wcult​
- If you must score in raw units, use wdist⋅Di+wcult⋅Ciw_{\text{dist}}\cdot D_i+w_{\text{cult}}\cdot C_iwdist​⋅Di​+wcult​⋅Ci​; ranking will match normalized ordering if both normalizations are monotone.
    

**Edge cases & correctness**
- **No interior breakpoints** → only two distinct orders: pure distance (t=0) and pure culture (t=1).
- **Numerical stability**: use an ε\varepsilonε around 0 and 1; treat near-parallel as “no cross.”
- **Ties**: keep deterministic tie-breakers (e.g., by distance then culture).
- **Complexity**: breakpoint calc is O(n2)O(n^2)O(n2); sorting steps O(nlog⁡n)O(n\log n)O(nlogn). For nnn in the tens/hundreds, this is fine. Cache per dataset/normalization.
    

**Why it feels great in UI**
- The order is constant between breakpoints; you only sample from those intervals.
- Every tick is a **new permutation**—no placebo.
- Ends are exact identities: t=0t=0t=0 = pure distance, t=1t=1t=1 = pure culture.
    

**Optional vector view (same idea)**
- Let xi=[di,ci]Tx_i=[d_i,c_i]^Txi​=[di​,ci​]T, w(t)=[1−t, t]Tw(t)=[1-t,\ t]^Tw(t)=[1−t, t]T.
- si(t)=w(t)Txis_i(t)=w(t)^T x_isi​(t)=w(t)Txi​.
- Breakpoints are where two projections are equal.
- In 2D these are the line crossings above; in higher-D it generalizes to hyperplanes (we’re staying 2D here).