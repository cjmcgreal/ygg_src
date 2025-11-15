# Navigation Structure

This document explains the two-level navigation pattern used in the application.

## Navigation Hierarchy

```
┌─────────────────────────────────────────────────────────────┐
│  SIDEBAR (Page Navigation)                                   │
│  ┌──────────────────┐                                        │
│  │ 🏠 Personal      │                                        │
│  │    Dashboard     │                                        │
│  │ 🌳 Trees         │                                        │
│  │ 💪 Exercise      │ ← Selected page                        │
│  │ 💰 Finance       │                                        │
│  │ ✅ Task Manager  │                                        │
│  │ ✈️ Travel        │                                        │
│  └──────────────────┘                                        │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  MAIN CONTENT AREA                                           │
│                                                              │
│  Exercise Tracker                                            │
│  ┌─────────────┬──────────────┬──────────────┐              │
│  │  Overview   │ Exercise Data│  Analytics   │ ← Domain tabs│
│  └─────────────┴──────────────┴──────────────┘              │
│                                                              │
│  [Content for selected tab]                                 │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Level 1: Sidebar Page Navigation

**Location**: Left sidebar
**Control**: Streamlit's built-in page navigation
**Purpose**: Switch between major functional areas (domains)
**Benefits**:
- URL routing (each page has its own URL)
- Browser back/forward buttons work
- Direct linking to specific domains

Available pages:
- **🏠 Personal Dashboard** - Home page (app.py)
- **🌳 Trees** - Tree visualization (pages/1_🌳_Trees.py)
- **💪 Exercise** - Exercise tracking (pages/2_💪_Exercise.py)
- **💰 Finance** - Financial tracking (pages/3_💰_Finance.py)
- **✅ Task Manager** - Task management (pages/4_✅_Task_Manager.py)
- **✈️ Travel** - Travel planning (pages/5_✈️_Travel.py)

## Level 2: Domain Tabs (Optional)

**Location**: Within the main content area
**Control**: Streamlit tabs
**Purpose**: Organize sub-sections within a domain

Example (Exercise domain):
- **Overview** - Introduction and quick links
- **Exercise Data** - View and manage exercise logs
- **Analytics** - Charts and insights

## Implementation Pattern

### In app.py (Home Page):
```python
# Home page content
st.title("🏠 Personal Dashboard")
st.write("Welcome to your personal dashboard!")

# Navigation happens automatically via pages/ folder
```

### In pages/2_💪_Exercise.py (Example Page):
```python
import streamlit as st
import sys
import os

# Add parent directory to path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from domains.exercise.exercise_app import render_exercise_app

# Page config
st.set_page_config(page_title="Exercise", page_icon="💪", layout="wide")

# Render the domain
render_exercise_app()
```

### In {domain}_app.py (Domain level):
```python
def render_exercise_app():
    st.header("Exercise Tracker")

    # Optional: Create tabs within this domain
    tab1, tab2, tab3 = st.tabs(["Overview", "Exercise Data", "Analytics"])

    with tab1:
        # Overview content
        pass

    with tab2:
        # Exercise data content
        pass

    with tab3:
        # Analytics content
        pass
```

## Benefits of This Pattern

1. **Clear Hierarchy**: Sidebar pages for major sections, tabs for sub-sections
2. **URL Routing**: Each page has its own URL for bookmarking and sharing
3. **Browser Integration**: Back/forward buttons work naturally
4. **Flexibility**: Domains can choose to use tabs or not
5. **Familiar UX**: Standard Streamlit multi-page app pattern
6. **Scalability**: Easy to add new domains by creating new page files
7. **Clean Code**: Each domain controls its own internal navigation
8. **Automatic Navigation**: Streamlit generates sidebar navigation automatically

## Adding Navigation to Your Domain

### Without Tabs (Simple domain):
```python
def render_my_domain_app():
    st.header("My Domain")
    st.write("Simple content without tabs")
    # All content here
```

### With Tabs (Complex domain):
```python
def render_my_domain_app():
    st.header("My Domain")

    tab1, tab2 = st.tabs(["Section 1", "Section 2"])

    with tab1:
        st.write("Section 1 content")

    with tab2:
        st.write("Section 2 content")
```

## Best Practices

1. **Use tabs sparingly** - Only when you have 2+ distinct sub-sections
2. **Keep tab names short** - 1-2 words maximum
3. **Logical grouping** - Tab content should be clearly related
4. **Consistent pattern** - If one domain uses tabs, others should follow similar patterns
5. **Avoid deep nesting** - Don't put tabs within tabs (keeps UI simple)
