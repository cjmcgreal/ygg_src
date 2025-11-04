---
id: task-001                           # Unique ID used in Mermaid (must be unique in Gantt chart)
title: Implement Feature Alpha        # Human-readable label
start: 2025-08-01                     # Start date in YYYY-MM-DD format
duration: 2d                          # Duration (e.g., 2d = 2 days, 4h = 4 hours)
depends_on: [decision]               # Optional list of task IDs this depends on
section: Primary Path                 # Gantt chart section name
status: active                        # Optional: e.g., active, done, crit (for critical path)
diagram_type: gantt                  # Used by the Python generator to filter tasks
---

### Notes

- This task will appear in the "Primary Path" section of the generated Gantt chart.
- You can link it to other tasks using the `depends_on` field.
- Set `status` to `active` to highlight it in the chart.
