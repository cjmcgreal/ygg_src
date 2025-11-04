import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from io import StringIO
import modules.animated as animated
import modules.utils as utils

#import hlidskjalf.depends.modules.animated as animated
#import hlidskjalf.depends.modules.utils as utils

# Remove whitespace from the top of the page and sidebar
st.set_page_config(layout="wide",
                   initial_sidebar_state="collapsed")
st.markdown("""
        <style>
               .block-container {
                    padding-top: 1rem;
                    padding-bottom: 0rem;
                    padding-left: 5rem;
                    padding-right: 5rem;
                }
        </style>
        """, unsafe_allow_html=True)
st.markdown(
    """
    <style>
        section[data-testid="stSidebar"] {
            width: 100px !important; # Set the width to your desired value
        }
    </style>
    """,
    unsafe_allow_html=True,
)
st.title("Yggdrasill")

#@st.cache_data(show_spinner="Loading the CSV file...")
# def load_csv(filename):
#     return pd.read_csv(filename).convert_dtypes()

# Default file paths
parent_tree_path = utils.getFullPath("data/parent_tree.csv")
prereq_tree_path = utils.getFullPath("data/prereq_tree.csv")
default_path = utils.getFullPath("data/driven_by_tree.csv")
template_tree_path = utils.getFullPath("data/template_tree.csv")

# Display them side by side
col1, col2, col3, col4 = st.columns(4)

# todo: make a function for each.
with col1:
    st.markdown("#### by Product Parent `parent`")
    st.markdown("##### as developer, where is the file I need?")
    df2 = pd.read_csv(parent_tree_path).convert_dtypes()
    child_col = df2.columns[0]
    parent_col = df2.columns[1]
    df2 = df2[[child_col, parent_col]]
    tree2_path = animated.makeCollapsibleTree(df2)
    with open(tree2_path, 'r', encoding='utf-8') as f:
        components.html(f.read(), height=2200, width=1000)
    
with col2:
    st.markdown("#### by Prerequisite")
    st.markdown("##### what task should I work on next?")
    df3 = pd.read_csv(prereq_tree_path).convert_dtypes()
    child_col = df3.columns[0]
    parent_col = df3.columns[1]
    df3 = df3[[child_col, parent_col]]
    tree3_path = animated.makeCollapsibleTree(df3)
    with open(tree3_path, 'r', encoding='utf-8') as f:
        components.html(f.read(), height=2200, width=1000)

with col3:
    st.markdown("#### by Driver `driven_by`")
    st.markdown("##### why is this needed?")
    df = pd.read_csv(default_path).convert_dtypes()
    child_col = df.columns[0]
    parent_col = df.columns[1]
    df = df[[child_col, parent_col]]
    tree1_path = animated.makeCollapsibleTree(df)
    with open(tree1_path, 'r', encoding='utf-8') as f:
        components.html(f.read(), height=2200, width=1000)
    
with col4:
    st.markdown("#### Templates")
    st.markdown("##### for reference")
    df4 = pd.read_csv(template_tree_path).convert_dtypes()
    child_col = df4.columns[0]
    parent_col = df4.columns[1]
    df4 = df4[[child_col, parent_col]]
    tree4_path = animated.makeCollapsibleTree(df4)
    with open(tree4_path, 'r', encoding='utf-8') as f:
        components.html(f.read(), height=2200, width=1000)
        