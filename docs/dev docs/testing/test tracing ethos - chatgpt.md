---
parent: yggdrasill
---


Does this give you enough information to build a tree where I can see a product, the associated requirements, and the tests that go with those requirements, and the code that implements those requirements: Line-by-line coverage, HTML reports showing which tests touch which lines

###### ChatGPT said:

Yes — you're **almost there**, but here’s the key distinction:

---

### ❗ The **coverage.py + pytest-cov** tools give you:

- **Line-by-line coverage** (✅)
    
- **Which lines are executed by the test suite** (✅)
    
- **An HTML report showing which lines were executed** (✅)
    
- But **they do _not_ tell you** _which specific test function_ executed which specific line (❌ _out of the box_)
    

---

### So can we build a complete **Product → Requirement → Test → Code** tree?

|Link|Can it be built?|Method|
|---|---|---|
|✅ Product → Requirement|Yes|Manual mapping (e.g., `PRODUCT-01` maps to `FR-001`, `FR-002`, etc.)|
|✅ Requirement → Test(s)|Yes|Use consistent IDs in test docstrings (`FR-001`)|
|⚠️ Test → Code (line-by-line)|_Not natively_|`coverage.py` shows lines hit, but not _which test hit them_|
|✅ Code (line) → Test (somewhat)|Yes via coverage total|“This line was covered” — but not by _which_ test|
|✅ Test → Code (by inspection)|Yes|Map by reading the test and seeing what it calls|

---

## 🔧 How to Fix That Missing Link (Test → Line-Level Mapping)

To get exact **Test Function ↔ Line-Level Code** mapping, you need one of:

### 1. `pytest-trace`

- Captures _which test covers which lines_.
    
- Generates output you can parse to build that tree.
    

> [https://github.com/anntzer/pytest-trace](https://github.com/anntzer/pytest-trace)  
> Output includes trace data of which test hit which line.

---

### 2. `pytest-cov --cov-context=test`

As of newer `coverage.py` versions:

bash

CopyEdit

`pytest --cov=my_module --cov-context=test`

- This captures **which test covers which line**.
    
- You'll see each line in the HTML report annotated with the name of the test function(s) that touched it.
    
- 🔥 This _is exactly_ what you want.
    

Then you can parse the output and generate a structure like:

yaml

CopyEdit

`PRODUCT-01:   - FR-001:       - tests/test_progression.py::test_progression_triggers_on_successful_sets       - Covered Lines:           - my_module/progression_engine.py: 42-47`

---

## ✅ Conclusion

### Can you build the tree? YES, with some help:

**Requirements to Tests:** Use tags like `FR-001` in test docstrings  
**Tests to Code Lines:** Use `--cov-context=test` to extract test coverage per line  
**Visualization:** Build a YAML/JSON or Mermaid structure from the output

---

## ✅ Example Mermaid Tree (After Trace Info)

mermaid

CopyEdit

`graph TD     P1[Product: Smart Progression Planner]     R1[FR-001: Trigger progression on success]     R2[FR-002: Trigger deload on failure]     T1[test_progression_triggers_on_successful_sets]     T2[test_deload_after_multiple_failures]     C1[calculate_next_weight (L42–L47)]     C2[trigger_deload (L51–L58)]      P1 --> R1     P1 --> R2     R1 --> T1     R2 --> T2     T1 --> C1     T2 --> C2`