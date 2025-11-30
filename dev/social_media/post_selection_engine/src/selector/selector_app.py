"""
Streamlit UI for the post selection engine.

Provides 4 tabs:
1. Run Draw - Execute probabilistic draw with effort filter
2. Post Ideas - Browse and filter all post ideas
3. History - View posting history and statistics
4. Probability Tree - View and edit probability weights
"""

import streamlit as st
import pandas as pd

from . import selector_workflow as workflow


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if 'draw_result' not in st.session_state:
        st.session_state.draw_result = None

    if 'last_recorded' not in st.session_state:
        st.session_state.last_recorded = None


def render_selector():
    """
    Main entry point for the selector UI.
    Called by app.py to render the full interface.
    """
    initialize_session_state()

    st.title("Social Media Post Selector")
    st.markdown("Probabilistic post selection with recency penalties")

    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "Run Draw",
        "Post Ideas",
        "History",
        "Probability Tree"
    ])

    with tab1:
        render_tab_run_draw()

    with tab2:
        render_tab_post_ideas()

    with tab3:
        render_tab_history()

    with tab4:
        render_tab_probability_tree()


# =============================================================================
# Tab 1: Run Draw
# =============================================================================

def render_tab_run_draw():
    """Tab 1: Execute draws and record posts."""
    st.header("Run Draw")

    # Effort filter section
    st.subheader("Effort Filter")
    col1, col2 = st.columns(2)
    with col1:
        min_effort = st.slider("Minimum Effort", 1, 5, 1, key="draw_min_effort")
    with col2:
        max_effort = st.slider("Maximum Effort", 1, 5, 5, key="draw_max_effort")

    # Validate effort range
    if min_effort > max_effort:
        st.warning("Minimum effort cannot be greater than maximum effort.")
        return

    # Run draw button
    if st.button("Run Draw", type="primary", use_container_width=True):
        with st.spinner("Running probabilistic draw..."):
            result = workflow.execute_draw(min_effort=min_effort, max_effort=max_effort)
            st.session_state.draw_result = result

    # Display results
    if st.session_state.draw_result is not None:
        result = st.session_state.draw_result

        if result['success']:
            st.success(f"Selected: **{result['topic']}** > **{result['subtopic']}**")

            # Show matching posts
            st.subheader("Matching Post Ideas")
            matching_posts = result['matching_posts']

            if len(matching_posts) > 0:
                # Display posts table
                display_df = matching_posts[['id', 'title', 'effort', 'status']].copy()
                st.dataframe(display_df, use_container_width=True, hide_index=True)

                # Show descriptions in expander
                with st.expander("View Post Descriptions"):
                    for _, post in matching_posts.iterrows():
                        st.markdown(f"**{post['title']}** (Effort: {post['effort']})")
                        st.markdown(f"_{post['description']}_")
                        st.divider()
            else:
                st.info("No draft posts match this subtopic and effort range.")

            # Record as posted button
            st.subheader("Record Selection")
            if st.button("Record as Posted", type="secondary"):
                success, msg = workflow.record_selection(
                    result['topic'],
                    result['subtopic']
                )
                if success:
                    st.success(msg)
                    st.session_state.last_recorded = {
                        'topic': result['topic'],
                        'subtopic': result['subtopic']
                    }
                    # Clear draw result to reset UI
                    st.session_state.draw_result = None
                    st.rerun()
                else:
                    st.error(msg)

            # Show probability details in expander
            with st.expander("View Adjusted Probabilities"):
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("**Topic Probabilities (after penalties)**")
                    topic_probs = result['adjusted_topic_probs']
                    prob_df = pd.DataFrame([
                        {'Topic': k, 'Probability': f"{v:.4f}"}
                        for k, v in sorted(topic_probs.items(), key=lambda x: -x[1])
                    ])
                    st.dataframe(prob_df, use_container_width=True, hide_index=True)

                with col2:
                    st.markdown("**Subtopic Probabilities (after penalties)**")
                    sub_probs = result['adjusted_subtopic_probs']
                    sub_df = pd.DataFrame([
                        {'Subtopic': k, 'Probability': f"{v:.4f}"}
                        for k, v in sorted(sub_probs.items(), key=lambda x: -x[1])
                    ])
                    st.dataframe(sub_df, use_container_width=True, hide_index=True)

        else:
            st.error(f"Draw failed: {result['error']}")

    # Show last recorded if exists
    if st.session_state.last_recorded:
        st.info(
            f"Last recorded: {st.session_state.last_recorded['topic']} > "
            f"{st.session_state.last_recorded['subtopic']}"
        )


# =============================================================================
# Tab 2: Post Ideas
# =============================================================================

def render_tab_post_ideas():
    """Tab 2: Browse and filter post ideas."""
    st.header("Post Ideas")

    # Filters
    col1, col2, col3 = st.columns(3)

    with col1:
        topics = ["All"] + workflow.get_all_topics()
        selected_topic = st.selectbox("Topic", topics, key="posts_topic_filter")

    with col2:
        if selected_topic == "All":
            subtopics = ["All"]
        else:
            subtopics = ["All"] + workflow.get_subtopics_for_topic(selected_topic)
        selected_subtopic = st.selectbox("Subtopic", subtopics, key="posts_subtopic_filter")

    with col3:
        effort_range = st.slider(
            "Effort Range",
            1, 5, (1, 5),
            key="posts_effort_filter"
        )

    # Get filtered posts
    topic_filter = None if selected_topic == "All" else selected_topic
    subtopic_filter = None if selected_subtopic == "All" else selected_subtopic

    posts_df = workflow.get_all_posts_filtered(
        topic=topic_filter,
        subtopic=subtopic_filter,
        min_effort=effort_range[0],
        max_effort=effort_range[1]
    )

    # Display count
    st.markdown(f"**{len(posts_df)} posts found**")

    # Display posts
    if len(posts_df) > 0:
        # Reorder columns for display
        display_cols = ['id', 'title', 'topic', 'subtopic', 'effort', 'status']
        st.dataframe(
            posts_df[display_cols],
            use_container_width=True,
            hide_index=True,
            height=400
        )

        # Expandable descriptions
        with st.expander("View Post Descriptions"):
            for _, post in posts_df.iterrows():
                st.markdown(f"**[{post['id']}] {post['title']}**")
                st.markdown(f"_{post['topic']} > {post['subtopic']}_ | Effort: {post['effort']}")
                st.markdown(post['description'])
                st.divider()
    else:
        st.info("No posts match the current filters.")


# =============================================================================
# Tab 3: History
# =============================================================================

def render_tab_history():
    """Tab 3: View posting history and statistics."""
    st.header("Posting History")

    # Recent posts section
    st.subheader("Recent Posts")
    recent_df = workflow.get_recent_post_history(20)

    if len(recent_df) > 0:
        st.dataframe(recent_df, use_container_width=True, hide_index=True)
    else:
        st.info("No posting history yet.")

    # Statistics section
    st.subheader("Topic Statistics")
    topic_stats = workflow.get_topic_statistics()

    if len(topic_stats) > 0:
        st.dataframe(topic_stats, use_container_width=True, hide_index=True)

        # Bar chart of topic frequency
        st.bar_chart(topic_stats.set_index('topic')['post_count'])
    else:
        st.info("No statistics available yet.")

    # Subtopic statistics
    st.subheader("Subtopic Statistics")
    subtopic_stats = workflow.get_subtopic_statistics()

    if len(subtopic_stats) > 0:
        st.dataframe(subtopic_stats, use_container_width=True, hide_index=True, height=300)
    else:
        st.info("No subtopic statistics available yet.")

    # Effort distribution
    st.subheader("Post Effort Distribution")
    effort_summary = workflow.get_effort_summary()
    st.dataframe(effort_summary, use_container_width=True, hide_index=True)

    effort_analysis = workflow.get_effort_analysis()
    st.metric("Average Post Effort", f"{effort_analysis['average_effort']:.2f}")


# =============================================================================
# Tab 4: Probability Tree
# =============================================================================

def render_tab_probability_tree():
    """Tab 4: View and edit probability tree."""
    st.header("Probability Tree")

    # Load current tree
    tree = workflow.get_probability_tree()

    # Topic probabilities section
    st.subheader("Topic Probabilities")
    st.markdown("Probabilities must sum to 1.0")

    # Create editable topic probabilities
    topic_data = []
    for topic_name, topic_info in tree['topics'].items():
        topic_data.append({
            'Topic': topic_name,
            'Probability': topic_info['probability'],
            'Subtopics': len(topic_info['subtopics'])
        })

    topic_df = pd.DataFrame(topic_data)

    # Display with data editor
    edited_topics = st.data_editor(
        topic_df,
        use_container_width=True,
        hide_index=True,
        disabled=['Topic', 'Subtopics'],
        key="topic_editor"
    )

    # Show sum validation
    topic_sum = edited_topics['Probability'].sum()
    if abs(topic_sum - 1.0) < 0.001:
        st.success(f"Topic probabilities sum to {topic_sum:.4f}")
    else:
        st.warning(f"Topic probabilities sum to {topic_sum:.4f} (should be 1.0)")

    # Subtopic probabilities section
    st.subheader("Subtopic Probabilities")

    # Select topic to view/edit subtopics
    selected_topic = st.selectbox(
        "Select topic to view subtopics",
        list(tree['topics'].keys()),
        key="subtopic_view_topic"
    )

    if selected_topic:
        subtopic_info = tree['topics'][selected_topic]['subtopics']
        subtopic_data = [
            {'Subtopic': name, 'Probability': prob}
            for name, prob in subtopic_info.items()
        ]
        subtopic_df = pd.DataFrame(subtopic_data)

        # Display with data editor
        edited_subtopics = st.data_editor(
            subtopic_df,
            use_container_width=True,
            hide_index=True,
            disabled=['Subtopic'],
            key=f"subtopic_editor_{selected_topic}"
        )

        # Show sum validation for subtopics
        subtopic_sum = edited_subtopics['Probability'].sum()
        if abs(subtopic_sum - 1.0) < 0.001:
            st.success(f"Subtopic probabilities sum to {subtopic_sum:.4f}")
        else:
            st.warning(f"Subtopic probabilities sum to {subtopic_sum:.4f} (should be 1.0)")

    # Save changes button
    st.divider()
    if st.button("Save Changes", type="primary"):
        # Build updated tree
        new_tree = {'topics': {}}

        for _, row in edited_topics.iterrows():
            topic_name = row['Topic']
            new_tree['topics'][topic_name] = {
                'probability': row['Probability'],
                'subtopics': tree['topics'][topic_name]['subtopics'].copy()
            }

        # Update subtopics for the currently selected topic
        if selected_topic:
            new_subtopics = {}
            for _, row in edited_subtopics.iterrows():
                new_subtopics[row['Subtopic']] = row['Probability']
            new_tree['topics'][selected_topic]['subtopics'] = new_subtopics

        # Save
        success, msg = workflow.save_full_probability_tree(new_tree)
        if success:
            st.success(msg)
            st.rerun()
        else:
            st.error(msg)

    # Manual record section
    st.divider()
    st.subheader("Manual Record Post")
    st.markdown("Record a post that was made outside this tool")

    col1, col2 = st.columns(2)
    with col1:
        manual_topic = st.selectbox(
            "Topic",
            list(tree['topics'].keys()),
            key="manual_topic"
        )
    with col2:
        manual_subtopics = list(tree['topics'][manual_topic]['subtopics'].keys())
        manual_subtopic = st.selectbox(
            "Subtopic",
            manual_subtopics,
            key="manual_subtopic"
        )

    if st.button("Record Post"):
        success, msg = workflow.record_selection(manual_topic, manual_subtopic)
        if success:
            st.success(msg)
        else:
            st.error(msg)


# =============================================================================
# Standalone Test Section
# =============================================================================

if __name__ == "__main__":
    # This file is meant to be imported by app.py
    # But we can test components here
    print("=" * 60)
    print("selector_app.py")
    print("=" * 60)
    print("\nThis module provides the render_selector() function.")
    print("Run the main app.py with: streamlit run app.py")
    print("\nComponents:")
    print("  - render_tab_run_draw()")
    print("  - render_tab_post_ideas()")
    print("  - render_tab_history()")
    print("  - render_tab_probability_tree()")
