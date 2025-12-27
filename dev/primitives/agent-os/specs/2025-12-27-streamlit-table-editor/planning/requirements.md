# Spec Requirements: Streamlit Table Editor Primitive

## Initial Description
I want to build a "primitive" i.e. an example of a pattern for agents and developers to build off of. In particular I want this to be a streamlit-based table editor. In the future, I want to be able to edit any table of backend table (postgres, sql, whatever), but for this initial demo of the pattern, it needs only to support csv. The table editor should use the streamlit st.data_editor object. It needs to be easy to add new columns, perhaps with an "add column" button. I want to be able to choose which table (i.e. csv file) to open. I want it to remember files I have opened. I want a feature where it keeps track of unique values of each column, and if I try to add a value that doesn't exist yet, it asks me to confirm. This "confirmation feature" should be configurable, i.e. be able to turn it off and on in the streamlit sidebar.

## Requirements Discussion

### First Round Questions

**Q1:** I assume the "add column" feature should prompt for a column name and data type (text, number, date, etc.). Is that correct, or should it default to text-only columns for simplicity in this initial version?
**Answer:** Text only for this initial version.

**Q2:** For the "remember files I have opened" feature, I'm thinking we store a list of recently opened file paths in a JSON or text file that persists between sessions. Should this also display the last-modified timestamp, or just the file paths? And should there be a limit (e.g., last 10 files)?
**Answer:** Yes, display last-modified timestamp. No limit on number of files remembered.

**Q3:** When detecting a new unique value in a column, I assume the confirmation should be a modal/popup that shows something like "Value 'X' is new for column 'Y'. Add it?" with Confirm/Cancel buttons. Is that the right approach, or would you prefer inline warnings?
**Answer:** Yes, this should be a popup.

**Q4:** I assume the table editor should support standard operations: add rows, delete rows, edit cells, and add columns. Should it also support deleting columns, or is that out of scope for this initial version?
**Answer:** Yes, support deleting columns. Include a popup confirmation when deleting columns.

**Q5:** For saving changes, I'm thinking of an explicit "Save" button rather than auto-save (to avoid accidental overwrites). Should there also be a "Save As" option to save to a new file, or just overwrite the original?
**Answer:** Have an explicit Save button as well as a Save As option.

**Q6:** Since this is a "primitive" meant to be a pattern for developers, I assume you want the code structured so the CSV handling is abstracted behind an interface that could later be swapped for PostgreSQL/SQL. Should I document this abstraction layer explicitly in the code, or just structure it cleanly for future extension?
**Answer:** There should be a dedicated DB class object that handles all database read and write. In principle this object could be used, in the future, by other processes.

**Q7:** For choosing which CSV file to open, should this be a file path text input, a file browser (using `st.file_uploader`), or both? Note: `st.file_uploader` uploads a copy while a path input would open files directly from disk.
**Answer:** There should be a file browser (user doesn't want to type in the path, but rather select the file from an explorer-type interface), but it should open directly from disk.

**Q8:** Is there anything specific you want to explicitly exclude from this initial version? For example: column reordering, column renaming, data validation beyond the unique-value confirmation, undo/redo, etc.?
**Answer:** No explicit exclusions.

### Existing Code to Reference

No similar existing features identified for reference.

### Follow-up Questions

**Follow-up 1:** Streamlit's built-in `st.file_uploader` creates a copy of the file rather than opening from disk directly. To open files directly from disk with a browser-like interface, we have a few options:
- Option A: Use a text input for the directory path, then show a dropdown/selectbox of CSV files found in that directory
- Option B: Use a third-party component like `streamlit-file-browser` (requires additional dependency)
- Option C: Allow the user to configure a "working directory" in the sidebar, then list all CSV files from that directory for selection

**Answer:** Option C - Allow the user to configure a "working directory" in the sidebar, then list all CSV files from that directory for selection.

## Visual Assets

### Files Provided:
No visual assets provided.

### Visual Insights:
N/A

## Requirements Summary

### Functional Requirements

**File Management**
- Configure a "working directory" via sidebar text input
- Display list of all CSV files found in the working directory for selection
- Remember previously opened files with their last-modified timestamps (persisted between sessions)
- No limit on number of remembered files
- Open files directly from disk (not uploaded copies)

**Table Editing (using st.data_editor)**
- View and edit CSV data in a tabular format
- Add new rows
- Delete existing rows
- Edit cell values inline
- Add new columns (text type only for this version)
- Delete columns with popup confirmation

**Unique Value Confirmation Feature**
- Track unique values for each column in the loaded table
- When user enters a value that doesn't exist in that column, show popup confirmation
- Popup should display: "Value 'X' is new for column 'Y'. Add it?" with Confirm/Cancel options
- Feature is configurable: can be toggled on/off via sidebar setting

**Save Operations**
- Explicit "Save" button to overwrite the original file
- "Save As" option to save to a new file
- No auto-save (to prevent accidental overwrites)

### Non-Functional Requirements

**Architecture & Extensibility**
- Dedicated DB class object that abstracts all database read/write operations
- DB class should be designed for potential reuse by other processes
- Structure should allow future extension to PostgreSQL, SQL, or other backends
- Code should serve as a "primitive" / pattern for agents and developers to build upon

**Code Quality**
- Follow single responsibility principle for components
- Clear separation between UI layer and data layer
- Well-documented code suitable as a reference implementation

### Reusability Opportunities

- DB class object designed for standalone use by other processes
- Pattern can be extended to support other database backends
- Unique value confirmation logic could be extracted for other data validation use cases

### Scope Boundaries

**In Scope:**
- CSV file support only (for this initial version)
- Text-only column types when adding new columns
- Working directory-based file browser
- Persistent file history with timestamps
- Unique value confirmation with toggle
- Add/delete rows
- Add/delete columns (with confirmation for delete)
- Edit cells
- Save and Save As functionality
- Sidebar configuration panel

**Out of Scope (for initial version, but architecture should support future addition):**
- PostgreSQL/SQL database support (future)
- Multiple column data types (future)
- Column reordering (not explicitly excluded, implement if straightforward)
- Column renaming (not explicitly excluded, implement if straightforward)
- Undo/redo functionality (not explicitly excluded)
- Data validation beyond unique value confirmation

### Technical Considerations

**Streamlit Components**
- Use `st.data_editor` for the main table editing interface
- Use sidebar (`st.sidebar`) for configuration options
- Use `st.text_input` for working directory configuration
- Use `st.selectbox` or similar for file selection from directory
- Use `st.dialog` or modal pattern for confirmation popups

**Data Persistence**
- Store recently opened files list in a JSON file
- Include file path and last-modified timestamp for each entry
- DB class handles all CSV read/write operations

**File System Operations**
- Scan working directory for .csv files
- Read CSV files directly from disk
- Write/overwrite CSV files on explicit save
- Get file modification timestamps for display

### UI Layout Concept

**Sidebar:**
- Working directory input
- File selector (dropdown of CSVs in working directory)
- Recently opened files list (with timestamps)
- Toggle for unique value confirmation feature
- Delete column controls (if applicable)

**Main Area:**
- st.data_editor displaying the loaded CSV
- Add Column button (prompts for column name)
- Add Row button
- Save button
- Save As button
