---
parent: yggdrasill
---
# Goal
Requirements and Test Tree -> make it easy to bidirectionally trace:
- Product -> requirements -> tests files and functions -> code lines files etc

# Implementation
### 2. `pytest-cov --cov-context=test`

As of newer `coverage.py` versions:
```bash pytest --cov=my_module --cov-context=test```

- This captures **which test covers which line**.    
- You'll see each line in the HTML report annotated with the name of the test function(s) that touched it.
- 🔥 This _is exactly_ what you want.

Then you can parse the output and generate a structure like:

yaml

CopyEdit

`PRODUCT-01:   - FR-001:       - tests/test_progression.py::test_progression_triggers_on_successful_sets       - Covered Lines:           - my_module/progression_engine.py: 42-47`