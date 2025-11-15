# Navigation Structure

This document explains the two-level navigation pattern used in the application.

## Navigation Hierarchy

```
┌─────────────────────────────────────────────────────────────┐
│  SIDEBAR (Domain Selection)                                  │
│  ┌──────────────────┐                                        │
│  │ ○ Trees          │                                        │
│  │ ● Exercise       │ ← Selected domain                      │
│  │ ○ Finance        │                                        │
│  │ ○ Task Manager   │                                        │
│  │ ○ Travel         │                                        │
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

## Level 1: Sidebar Domain Navigation

**Location**: Left sidebar
**Control**: Radio buttons
**Purpose**: Switch between major functional areas (domains)

Available domains:
- **Trees** - Tree visualization
- **Exercise** - Exercise tracking
- **Finance** - Financial tracking
- **Task Manager** - Task management
- **Travel** - Travel planning

## Level 2: Domain Tabs (Optional)

**Location**: Within the main content area
**Control**: Streamlit tabs
**Purpose**: Organize sub-sections within a domain

Example (Exercise domain):
- **Overview** - Introduction and quick links
- **Exercise Data** - View and manage exercise logs
- **Analytics** - Charts and insights

## Implementation Pattern

### In app.py (Root):
```python
# Sidebar for domain selection
with st.sidebar:
    selected_domain = st.radio(
        "Select Domain",
        options=["Trees", "Exercise", "Finance", "Task Manager", "Travel"]
    )

# Render selected domain
if selected_domain == "Exercise":
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

1. **Clear Hierarchy**: Sidebar for major sections, tabs for sub-sections
2. **Flexibility**: Domains can choose to use tabs or not
3. **Familiar UX**: Standard navigation pattern users expect
4. **Scalability**: Easy to add new domains or sub-sections
5. **Clean Code**: Each domain controls its own internal navigation

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
