# Initial Spec Idea

## User's Initial Description
I want to build a "primitive" i.e. an example of a pattern for agents and developers to build off of. In particular I want this to be a streamlit-based table editor. In the future, I want to be able to edit any table of backend table (postgres, sql, whatever), but for this initial demo of the pattern, it needs only to support csv. The table editor should use the streamlit st.data_editor object. It needs to be easy to add new columns, perhaps with an "add column" button. I want to be able to choose which table (i.e. csv file) to open. I want it to remember files I have opened. I want a feature where it keeps track of unique values of each column, and if I try to add a value that doesn't exist yet, it asks me to confirm. This "confirmation feature" should be configurable, i.e. be able to turn it off and on in the streamlit sidebar.

## Metadata
- Date Created: 2025-12-27
- Spec Name: streamlit-table-editor
- Spec Path: /home/conrad/git/ygg_src/dev/primitives/agent-os/specs/2025-12-27-streamlit-table-editor
