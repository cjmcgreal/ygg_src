---
type: procedure
domain: software
parent: yggdrasill
status: proposed
---

**Start the streamlit app python code** 
In the terminal:
```bash
conda activate sfs &&
cd ~/git/yggdrasill/yggdrasill/app/hlidskjalf/src/ &&
streamlit run app.py
```

# Diagram
WARNING -> THIS DIAGRAM MAINTAINED MANUALLY
```mermaid
sequenceDiagram
    participant User
    participant ygg
    participant start_app.sh
    participant load_obsidian_tree_prod.py
    participant app.py

    User->>ygg: enter "ygg" in terminal
    ygg->>start_app.sh: expand alias to run script
    start_app.sh->>load_obsidian_tree_prod.py: load tree data
    start_app.sh->>app.py: streamlit run app.py
```
