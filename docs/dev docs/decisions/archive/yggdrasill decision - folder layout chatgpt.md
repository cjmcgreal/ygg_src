---
type: decision
parent: yggdrasill
---
# Decision 2025-08-07
For now -> 
- collocate tests with code.
- documentation in it's own folder -> exposed as a streamlit tree

# Background
I'm back to talking about the "five folders" approach (source code, test folder, documentation folder, product management and task tree, runestone repo). Should I make the test and documentation folders subfolders of the source code folder? should I store the documentation of a particular python package in the same folder as that python file? same question with the testing

###### ChatGPT said:

Great question — and a very real architectural decision that affects how easily both humans and agents navigate your repo.

Let’s break it down.

---

## 🧭 First Principles

You’re balancing two core needs:

1. **Human ergonomics**  
    Easy to browse, write, and understand as a solo or team developer.
    
2. **Agent ergonomics**  
    Easy for AI to crawl, reason about, and retrieve the right test/docs/code clusters.
    

Also: you're building a **multi-domain**, **multi-repo** system. That means conventions matter more than ever, because you're going to want to automate chunking, traversal, and updates.

---

## 🔀 Option 1: Flat but Linked

**Keep these separate:**

- `/src/` — source code
    
- `/tests/` — matching test hierarchy
    
- `/docs/` — markdown documentation tree
    
- `/product/` — feature tree, task tracking
    
- `/runestone/` — orchestration layer
    

💡 Inside each folder, **mirror the structure** of `/src/`.

Example:

bash

CopyEdit

`/src/obsidian_qc/parser.py /tests/obsidian_qc/test_parser.py /docs/obsidian_qc/parser.md`

Then, link everything through:

- frontmatter
    
- naming conventions
    
- tree references
    

✅ Pros:

- Separation of concerns
    
- Easy batch processing (e.g. run all tests)
    
- Easier to manage CI/CD
    
- Obvious folder purposes
    

🚫 Cons:

- More duplication across folders
    
- Requires linking metadata to track relations
    

---

## 🧩 Option 2: Collocated Approach (Docs + Tests Inside Modules)

Store everything about a component/module in the same directory:

pgsql

CopyEdit

`/src/obsidian_qc/     ├── parser.py     ├── test_parser.py     ├── parser.md`

✅ Pros:

- Super convenient for local dev
    
- Easy to see code + doc + test all at once
    
- Easier for retrieval-based agents in small projects
    

🚫 Cons:

- Harder to automate global test discovery
    
- Risk of clutter
    
- Documentation can bloat source folders
    
- Harder to implement standardized tooling across repos
    

---

## 🧠 My Recommendation (TL;DR):

> 🟩 **Use Option 1**: keep `/tests/` and `/docs/` separate from `/src/`, but **mirror the directory structure** and use strong links between them.

Then:

- Use frontmatter in the markdown files to link to source/test paths.
    
- Use a component map (YAML or JSON) for AI traversal.
    
- Store longform **design intent** and **API usage examples** in `/docs`, not in code comments.
    
- Keep test logic in `/tests`, even for small functions — this will scale better as you delegate test generation to agents.
    

---

## 💬 Bonus Tip: Hybrid for Runestone-Specific Code

For the agent orchestration layer (`runestone/`), you _might_ choose to colocate things more tightly:

bash

CopyEdit

`/runestone/     ├── runestone_client.py     ├── test_runestone_client.py     ├── runestone_client.md`

Why? Because that part **isn't a reusable package**, it's a high-touch, evolving core of your agent tooling — and being able to see everything together can be helpful.

Want a starter component map or a template layout for this style?

##### You said:

let's say I have the tests in a separate folder, how do I add them to the path etc?

###### ChatGPT said:

If your tests live in a separate folder (e.g. `/tests`) and you're testing modules from your source code folder (e.g. `/src`), you’ll need to **add the source directory to `sys.path`** so Python knows where to find your modules when running tests.

Here’s how to do it cleanly:

---

### ✅ **Option 1: Add `/src` to `sys.path` inside `conftest.py` or at the top of each test file**

At the top of your test file(s) or a shared `conftest.py`, add this:

python

CopyEdit

`import sys import os  # Adds the /src directory to the Python path sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))`

This works for typical repo structure like:

bash

CopyEdit

`/myproject ├── src/ │   └── mymodule/ │       └── foo.py ├── tests/ │   ├── test_foo.py │   └── conftest.py`

Then in `test_foo.py`, you can import like:

python

CopyEdit

`from mymodule.foo import some_function`

---

### ✅ **Option 2: Set the `PYTHONPATH` when running tests**

From the command line:

bash

CopyEdit

`PYTHONPATH=src pytest tests/`

Or if using Windows CMD:

cmd

CopyEdit

`set PYTHONPATH=src && pytest tests/`

Or PowerShell:

powershell

CopyEdit

`$env:PYTHONPATH = "src"; pytest tests/`

Great for automation, e.g. in CI/CD pipelines.

---

### ✅ **Option 3: Use a test config file**

Create a `pytest.ini` or `pyproject.toml`:

#### `pytest.ini`

ini

CopyEdit

`[pytest] pythonpath = src`

#### Or in `pyproject.toml` (if using it)

toml

CopyEdit

`[tool.pytest.ini_options] pythonpath = ["src"]`

Then just run:

bash

CopyEdit

`pytest`

---

### TL;DR

For your Runestone system:

- ✅ Put `src` in the Python path using `sys.path.insert` or `PYTHONPATH`
    
- ✅ Use a `pytest.ini` to keep it clean and reproducible
    
- ✅ Imports in tests should be **absolute** (not relative), e.g. `from mymodule.foo import bar`
    

Want me to generate a `conftest.py` or a `pytest.ini` that fits your current structure?

##### You said:

Expand on the details of the cons of the collocated approach. In particular as it comes to tradeoffs related to scaling. I'm preferring this approach for now, keep in mind that right now I'm just a single developer manually running runestones and manually testing code before committing it. My sense is that once the repo gets very big, the flat approach is better but I'm trying to understand at what scale and size point the collocated approach becomes very painful. Harder to automate global test discovery Risk of clutter Documentation can bloat source folders Harder to implement standardized tooling across repos

###### ChatGPT said:

You're absolutely right to go with a collocated approach for now — especially as a solo dev managing everything manually. It keeps context tight, reduces friction, and fits naturally with how you're invoking Runestones and doing hands-on testing. But you’re also right to look ahead. Here’s a breakdown of **why** the collocated structure can become a liability _at scale_, and what the tradeoffs really are.

---

## ⚠️ Cons of Collocated Tests & Docs — And Why They Hurt at Scale

### 1. 🔍 **Harder to automate global test discovery**

**Why it matters:**

- Pytest and other tools usually expect a predictable test folder (`/tests`) to recurse into.
    
- If tests are scattered throughout `/src/**`, custom discovery logic becomes necessary.
    
- It’s easier to miss tests during CI runs, especially when you start excluding folders (e.g. generated code, legacy stuff).
    
- Tooling like coverage reports, test runners, or linters often break or need manual tuning.
    

**At scale:**

- One or two folders? No big deal.
    
- 50+ nested modules? Suddenly your test discovery script turns into a brittle liability.
    

**Workaround (but still painful):**

- Use `pytest --pyargs` and maintain a `__init__.py` trail everywhere.
    
- Or write a script to crawl `/src/**/test_*.py` manually. Sounds fun until it breaks silently.
    

---

### 2. 🧹 **Risk of clutter**

**Why it matters:**

- Tests, test data, markdown docs, and actual implementation code are very different beasts.
    
- If `mymodule/` contains `foo.py`, `test_foo.py`, `README.md`, `examples.ipynb`, `design.md`, `prototype_legacy.py`, etc… it becomes overwhelming to browse.
    
- Makes PRs noisier (harder to focus reviewer attention).
    

**At scale:**

- When contributors are working across different components, code readability and discoverability take a hit.
    
- Devs waste time mentally filtering through junk files to find the real ones.
    

**Also:**

- You start inventing naming schemes to compensate: `test_foo`, `foo_doc`, `foo_legacy_test`, etc.
    
- Eventually you're writing an internal "how to name files" doc… to fix a structure problem.
    

---

### 3. 🗃️ **Documentation can bloat source folders**

**Why it matters:**

- Design discussions, architecture notes, usage guides, and long-form thinking aren’t source code.
    
- These docs tend to grow organically and aren’t updated as reliably as code.
    
- You risk having multiple competing versions: `README.md`, `design_notes.md`, `API_USAGE.md`, etc.
    

**At scale:**

- 3–5 devs? Not a big deal.
    
- 20+ devs, multiple components? No one knows which document is canonical.
    
- Markdown version drift → outdated assumptions in code.
    

**Also:**

- You lose the ability to run automated documentation tools cleanly (e.g. mkdocs, Docusaurus) without custom file skipping logic.
    

---

### 4. 🛠️ **Harder to implement standardized tooling across repos**

**Why it matters:**

- Repos with `/src`, `/tests`, `/docs` folders are predictable for CI/CD, linting, formatting, release scripts, etc.
    
- Many tools assume or recommend this structure.
    
- Your collocated setup becomes an edge case that needs one-off glue everywhere.
    

**At scale:**

- When you start making reusable scripts for multi-repo pipelines, or onboarding new contributors/agents, you’ll be writing conditional logic just for your one-off folder tree.
    

**Symptoms:**

- Bash scripts with `if [ -f src/module/test_*.py ]; then ...`
    
- `exclude = */docs/*.md` regex gymnastics in `.flake8`, `.pylintrc`, or `.pre-commit-config.yaml`
    

---

## 🎯 When Does the Pain Begin?

Here's a rough gradient:

|Project Size|Team Size|Collocated Feels…|Why|
|---|---|---|---|
|< 2k LOC|Solo dev|✨ Efficient|Context is king.|
|~5–10k LOC|2–3 devs|🤔 Manageable|Navigation gets tricky, tooling still fine.|
|> 15k LOC|3+ devs|😖 Messy|Discoverability suffers, script complexity rises.|
|> 30k LOC|5+ devs|💀 Unscalable|Breaks automation, invites entropy.|

---

## 🧠 Strategic Takeaway for You

Stick with **collocated for now**, especially with Runestone keeping you close to the code and test generation process. But build with an eye toward modularity:

1. **Mark your collocated tests/docs with consistent naming** (e.g. `test_*.py`, `README.md`).
    
2. **Centralize config** in `pyproject.toml` or `pytest.ini` so switching later is easy.
    
3. **Abstract tooling** behind commands like `make test`, `make lint`, `make docs` so the internal paths are swappable.
    

Then, when the day comes that you need to split `/tests`, `/docs`, etc., you’ll barely feel the pain.

Want a migration playbook or a hybrid model suggestion next?

##### You said:

Help me understand (1) how do I ensure that the test, docs, and source folder structures mirror each other, (2) how do I use pyproject.toml or pytest.ini to centralize the config, (3) what is the intent via make test, make lint, make docs, (4) give me a basic outline of a migration playbook

###### ChatGPT said:

Great questions — these are exactly the right instincts if you’re building something solo but aiming for long-term scalability and automation. Let’s tackle each one methodically.

---

## ✅ (1) How to Ensure Test, Docs, and Source Structures Mirror Each Other

This means: for every module or package in your `src/`, there’s a corresponding structure in `tests/` and (optionally) `docs/`.

### 📁 Example Folder Structure

bash

CopyEdit

`/src/   runestone/     client.py     utils/       file_loader.py       tokenizer.py  /tests/   runestone/     test_client.py     utils/       test_file_loader.py       test_tokenizer.py  /docs/   runestone/     client.md     utils/       file_loader.md       tokenizer.md`

### 🛠 How to Enforce/Maintain This

- **Manual discipline at first:** Use naming conventions like `test_{module}.py` and matching folder names.
    
- **Automation (optional later):**
    
    - Write a script that traverses `src/` and verifies that each file has a corresponding `test_` file in `tests/`.
        
    - Similarly, verify that each `.py` has a `.md` in `docs/` if desired.
        

---

## 🔧 (2) How to Use `pyproject.toml` or `pytest.ini` to Centralize Config

### 🎯 Goal: Stop configuring tools piecemeal with flags or CLI arguments.

### ✅ `pytest.ini` Example

ini

CopyEdit

`# pytest.ini [pytest] testpaths = tests python_files = test_*.py python_classes = Test* python_functions = test_* addopts = --strict-markers --tb=short -ra`

### ✅ `pyproject.toml` Example (for tools like black, isort, mypy)

toml

CopyEdit

`[tool.black] line-length = 88 target-version = ['py311']  [tool.isort] profile = "black"  [tool.mypy] strict = true files = "src"  [tool.pytest.ini_options] testpaths = ["tests"] addopts = "--strict-markers"`

> Use `pytest.ini` if you're _only_ configuring pytest. Use `pyproject.toml` if you want a single file for everything (pytest, black, mypy, etc). Both approaches are fine — just pick one.

---

## 🧪 (3) What’s the Point of `make test`, `make lint`, `make docs`?

These are just aliases — they centralize your dev tasks behind consistent commands.

### 🧰 `Makefile` Example

makefile

CopyEdit

`.PHONY: test lint docs  test: 	pytest  lint: 	black src tests 	isort src tests 	flake8 src tests  docs: 	mkdocs build`

### ✅ Benefits:

- You hide tool-specific invocations behind memorable commands.
    
- Easy for contributors (or AI agents!) to run the right thing without knowing internal details.
    
- Easier to transition tools later (`pytest` → `nose`, `mkdocs` → `sphinx`, etc.)
    

---

## 📦 (4) Migration Playbook: From Collocated to Split Folder Structure

Here’s a simple step-by-step plan:

---

### **Step 1: Freeze the Current Structure**

- Create a backup branch (e.g., `backup/collocated-layout`).
    
- Lock in any important agent-generated files or docs.
    

---

### **Step 2: Define the Target Folder Tree**

bash

CopyEdit

`/src/   runestone/   /tests/   runestone/   /docs/   runestone/`

> Use your current folder structure as a guide.

---

### **Step 3: Write a Migration Script (Optional)**

Python script to:

- Move all `test_*.py` into `tests/` folder, preserving substructure.
    
- Move `*.md` docs into `docs/`, matched to module name.
    

---

### **Step 4: Update Config Files**

- Add or update `pytest.ini` or `pyproject.toml` with the correct `testpaths`.
    
- Update any CI workflows to use `pytest tests/` instead of scanning `src/`.
    

---

### **Step 5: Add a `Makefile`**

Use the template above. Start simple.

---

### **Step 6: Test the New Layout**

- Run `make test` and `make lint`.
    
- Spot-check a few doc files for broken links or paths.
    

---

### **Step 7: Clean Up**

- Remove test and doc files from `src/` if you haven’t already.
    
- Update documentation (maybe via Runestone) to reflect the new layout.
    

---

## ✅ Final Tip

If you're using Runestone agents to generate new code/tests/docs:

> Consider building a small router that _automatically_ files output into the correct `src/`, `tests/`, or `docs/` location based on filename patterns or agent metadata.

Let me know if you'd like a working script to automate the migration or a Runestone-compatible prompt template to guide agents in the new structure.