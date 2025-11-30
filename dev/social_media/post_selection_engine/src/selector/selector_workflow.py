"""
Workflow/orchestration layer for the post selection engine.

Acts as the "API interface" between the frontend (Streamlit) and backend layers.
Each frontend action has a dedicated function here that coordinates calls
to selector_db, selector_logic, and selector_analysis.
"""

from typing import Optional

import pandas as pd

from . import selector_db as db
from . import selector_logic as logic
from . import selector_analysis as analysis


# =============================================================================
# Draw Workflow
# =============================================================================

def execute_draw(
    min_effort: int = 1,
    max_effort: int = 5
) -> dict:
    """
    Execute a complete post selection draw workflow.

    This is the main workflow that:
    1. Loads the probability tree
    2. Gets recent post history (last 3)
    3. Runs the hierarchical draw with penalties
    4. Filters matching posts by effort
    5. Returns results

    Args:
        min_effort: Minimum effort level to include (1-5).
        max_effort: Maximum effort level to include (1-5).

    Returns:
        dict: Result with keys:
            - success: bool
            - topic: str (selected topic)
            - subtopic: str (selected subtopic)
            - matching_posts: pd.DataFrame (posts matching subtopic and effort)
            - adjusted_topic_probs: dict (for transparency)
            - adjusted_subtopic_probs: dict (for transparency)
            - error: str or None
    """
    try:
        # Load probability tree
        tree = db.load_probability_tree()

        # Validate tree
        is_valid, msg = logic.validate_probability_tree(tree)
        if not is_valid:
            return {
                'success': False,
                'topic': None,
                'subtopic': None,
                'matching_posts': pd.DataFrame(),
                'adjusted_topic_probs': {},
                'adjusted_subtopic_probs': {},
                'error': f"Invalid probability tree: {msg}"
            }

        # Get recent history
        recent_topics = db.get_recent_topics(3)
        recent_subtopics = db.get_recent_subtopics(3)

        # Run the draw
        selected_topic, selected_subtopic, debug_info = logic.run_hierarchical_draw(
            tree, recent_topics, recent_subtopics
        )

        if selected_topic is None or selected_subtopic is None:
            return {
                'success': False,
                'topic': selected_topic,
                'subtopic': selected_subtopic,
                'matching_posts': pd.DataFrame(),
                'adjusted_topic_probs': debug_info.get('adjusted_topic_probs', {}),
                'adjusted_subtopic_probs': debug_info.get('adjusted_subtopic_probs', {}),
                'error': debug_info.get('error', 'Unknown error during draw')
            }

        # Get matching posts filtered by subtopic and effort
        matching_posts = db.get_posts_filtered(
            subtopic=selected_subtopic,
            min_effort=min_effort,
            max_effort=max_effort,
            status='draft'
        )

        return {
            'success': True,
            'topic': selected_topic,
            'subtopic': selected_subtopic,
            'matching_posts': matching_posts,
            'adjusted_topic_probs': debug_info.get('adjusted_topic_probs', {}),
            'adjusted_subtopic_probs': debug_info.get('adjusted_subtopic_probs', {}),
            'error': None
        }

    except Exception as e:
        return {
            'success': False,
            'topic': None,
            'subtopic': None,
            'matching_posts': pd.DataFrame(),
            'adjusted_topic_probs': {},
            'adjusted_subtopic_probs': {},
            'error': str(e)
        }


def record_selection(topic: str, subtopic: str, posted_date: str = None) -> tuple[bool, str]:
    """
    Record that a topic/subtopic was posted.

    Args:
        topic: The topic that was posted.
        subtopic: The subtopic that was posted.
        posted_date: Optional date string (YYYY-MM-DD). Defaults to today.

    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        success, new_id = db.record_post(topic, subtopic, posted_date)

        if success:
            return True, f"Recorded post #{new_id}: {topic} -> {subtopic}"
        else:
            return False, "Failed to record post to history"

    except Exception as e:
        return False, f"Error recording post: {str(e)}"


# =============================================================================
# Post Browsing
# =============================================================================

def get_available_posts_for_subtopic(
    subtopic: str,
    min_effort: int = 1,
    max_effort: int = 5
) -> pd.DataFrame:
    """
    Get all available (draft) posts matching subtopic and effort criteria.

    Args:
        subtopic: The subtopic to filter by.
        min_effort: Minimum effort level.
        max_effort: Maximum effort level.

    Returns:
        pd.DataFrame: Matching posts.
    """
    return db.get_posts_filtered(
        subtopic=subtopic,
        min_effort=min_effort,
        max_effort=max_effort,
        status='draft'
    )


def get_all_posts_filtered(
    topic: Optional[str] = None,
    subtopic: Optional[str] = None,
    min_effort: int = 1,
    max_effort: int = 5
) -> pd.DataFrame:
    """
    Get posts with optional filters for browsing.

    Args:
        topic: Optional topic filter.
        subtopic: Optional subtopic filter.
        min_effort: Minimum effort level.
        max_effort: Maximum effort level.

    Returns:
        pd.DataFrame: Filtered posts.
    """
    return db.get_posts_filtered(
        topic=topic,
        subtopic=subtopic,
        min_effort=min_effort,
        max_effort=max_effort
    )


# =============================================================================
# History and Statistics
# =============================================================================

def get_recent_post_history(n: int = 20) -> pd.DataFrame:
    """
    Get recent post history for display.

    Args:
        n: Number of recent posts to retrieve.

    Returns:
        pd.DataFrame: Recent posts sorted by date descending.
    """
    return db.get_recent_posts(n)


def get_topic_statistics() -> pd.DataFrame:
    """
    Get posting statistics by topic.

    Returns:
        pd.DataFrame: Topic statistics.
    """
    history_df = db.load_post_history()
    return analysis.calculate_topic_statistics(history_df)


def get_subtopic_statistics() -> pd.DataFrame:
    """
    Get posting statistics by subtopic.

    Returns:
        pd.DataFrame: Subtopic statistics.
    """
    history_df = db.load_post_history()
    return analysis.calculate_subtopic_statistics(history_df)


def get_effort_analysis() -> dict:
    """
    Get effort distribution analysis.

    Returns:
        dict: Effort analysis results.
    """
    posts_df = db.load_posts()
    return analysis.analyze_effort_distribution(posts_df)


def get_effort_summary() -> pd.DataFrame:
    """
    Get effort distribution as DataFrame for display.

    Returns:
        pd.DataFrame: Effort level summary.
    """
    posts_df = db.load_posts()
    return analysis.get_effort_summary_df(posts_df)


def get_posting_trends(days: int = 30) -> pd.DataFrame:
    """
    Get posting trends over time.

    Args:
        days: Number of days to analyze.

    Returns:
        pd.DataFrame: Daily posting counts.
    """
    history_df = db.load_post_history()
    return analysis.get_posting_trends(history_df, days)


# =============================================================================
# Probability Tree Management
# =============================================================================

def get_topic_subtopic_overview() -> dict:
    """
    Get overview of all topics and subtopics with their probabilities.

    Returns:
        dict: Overview with topics, subtopics, and probabilities.
    """
    tree = db.load_probability_tree()
    history_df = db.load_post_history()

    # Get coverage summary
    coverage = analysis.get_coverage_summary(tree, history_df)

    # Build detailed topic info
    topics_info = []
    for topic_name, topic_data in tree['topics'].items():
        topic_info = {
            'name': topic_name,
            'probability': topic_data['probability'],
            'subtopics': []
        }

        for sub_name, sub_prob in topic_data['subtopics'].items():
            topic_info['subtopics'].append({
                'name': sub_name,
                'probability': sub_prob
            })

        topics_info.append(topic_info)

    return {
        'topics': topics_info,
        'coverage': coverage
    }


def get_probability_tree() -> dict:
    """
    Get the raw probability tree.

    Returns:
        dict: The probability tree.
    """
    return db.load_probability_tree()


def update_topic_probability(topic: str, new_probability: float) -> tuple[bool, str]:
    """
    Update a topic's probability.

    Note: This does not automatically normalize other topics.
    The caller should ensure all topic probabilities still sum to 1.

    Args:
        topic: Topic to update.
        new_probability: New probability value (0-1).

    Returns:
        tuple: (success: bool, message: str)
    """
    tree = db.load_probability_tree()

    success, msg = logic.update_probability_tree(tree, topic, new_topic_prob=new_probability)
    if not success:
        return False, msg

    # Save updated tree
    if db.save_probability_tree(tree):
        return True, f"Updated {topic} probability to {new_probability}"
    else:
        return False, "Failed to save probability tree"


def update_subtopic_probabilities(topic: str, subtopic_probs: dict) -> tuple[bool, str]:
    """
    Update subtopic probabilities for a topic.

    Args:
        topic: Topic to update.
        subtopic_probs: Dict mapping subtopic names to new probabilities.
                       Must sum to 1.0.

    Returns:
        tuple: (success: bool, message: str)
    """
    tree = db.load_probability_tree()

    success, msg = logic.update_probability_tree(tree, topic, subtopic_probs=subtopic_probs)
    if not success:
        return False, msg

    # Validate the updated tree
    is_valid, validation_msg = logic.validate_probability_tree(tree)
    if not is_valid:
        return False, f"Invalid update: {validation_msg}"

    # Save updated tree
    if db.save_probability_tree(tree):
        return True, f"Updated subtopic probabilities for {topic}"
    else:
        return False, "Failed to save probability tree"


def save_full_probability_tree(tree: dict) -> tuple[bool, str]:
    """
    Save a complete probability tree after validation.

    Args:
        tree: The complete probability tree to save.

    Returns:
        tuple: (success: bool, message: str)
    """
    # Validate first
    is_valid, msg = logic.validate_probability_tree(tree)
    if not is_valid:
        return False, f"Invalid tree: {msg}"

    if db.save_probability_tree(tree):
        return True, "Probability tree saved successfully"
    else:
        return False, "Failed to save probability tree"


# =============================================================================
# Utility Functions
# =============================================================================

def get_all_topics() -> list[str]:
    """Get list of all topic names."""
    return db.get_all_topics()


def get_subtopics_for_topic(topic: str) -> list[str]:
    """Get list of subtopics for a topic."""
    return db.get_subtopics_for_topic(topic)


# =============================================================================
# Standalone Test Section
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Testing selector_workflow.py")
    print("=" * 60)

    # Test execute_draw
    print("\n--- Testing Execute Draw ---")
    result = execute_draw(min_effort=1, max_effort=5)
    print(f"Success: {result['success']}")
    print(f"Selected: {result['topic']} -> {result['subtopic']}")
    print(f"Matching posts: {len(result['matching_posts'])}")

    if result['success']:
        print("\nAdjusted topic probabilities:")
        for topic, prob in sorted(result['adjusted_topic_probs'].items(), key=lambda x: -x[1])[:5]:
            print(f"  {topic}: {prob:.4f}")

    # Test with effort filter
    print("\n--- Testing Draw with Effort Filter (1-2) ---")
    result = execute_draw(min_effort=1, max_effort=2)
    print(f"Selected: {result['topic']} -> {result['subtopic']}")
    print(f"Matching posts (effort 1-2): {len(result['matching_posts'])}")

    # Test topic overview
    print("\n--- Topic Overview ---")
    overview = get_topic_subtopic_overview()
    print(f"Total topics: {overview['coverage']['total_topics']}")
    print(f"Total subtopics: {overview['coverage']['total_subtopics']}")

    # Test statistics
    print("\n--- Topic Statistics ---")
    topic_stats = get_topic_statistics()
    print(topic_stats)

    # Test effort analysis
    print("\n--- Effort Analysis ---")
    effort = get_effort_analysis()
    print(f"Average effort: {effort['average_effort']}")

    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)
