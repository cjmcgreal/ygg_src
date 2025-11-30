"""
Database layer for the post selection engine.

Handles all file I/O operations for:
- probability_tree.json (topic/subtopic hierarchy with probabilities)
- posts.csv (100 post ideas)
- post_history.csv (record of posted topics/subtopics)
"""

import json
import os
from datetime import datetime
from pathlib import Path

import pandas as pd


# Get the data directory path relative to this file
DATA_DIR = Path(__file__).parent / "selector_data"


# =============================================================================
# Probability Tree Operations
# =============================================================================

def load_probability_tree() -> dict:
    """
    Load the probability tree from JSON file.

    Returns:
        dict: Nested dictionary with topics and their subtopics with probabilities.
              Structure: {"topics": {"topic_name": {"probability": float, "subtopics": {...}}}}
    """
    tree_path = DATA_DIR / "probability_tree.json"

    with open(tree_path, 'r') as f:
        tree = json.load(f)

    return tree


def save_probability_tree(tree: dict) -> bool:
    """
    Save the probability tree to JSON file.

    Args:
        tree: Nested dictionary with topics and subtopics.

    Returns:
        bool: True if save was successful, False otherwise.
    """
    tree_path = DATA_DIR / "probability_tree.json"

    try:
        with open(tree_path, 'w') as f:
            json.dump(tree, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving probability tree: {e}")
        return False


def get_all_topics() -> list[str]:
    """
    Get list of all topic names.

    Returns:
        list: List of topic name strings.
    """
    tree = load_probability_tree()
    return list(tree["topics"].keys())


def get_subtopics_for_topic(topic: str) -> list[str]:
    """
    Get list of subtopics for a given topic.

    Args:
        topic: The topic name.

    Returns:
        list: List of subtopic name strings.
    """
    tree = load_probability_tree()

    if topic not in tree["topics"]:
        return []

    return list(tree["topics"][topic]["subtopics"].keys())


# =============================================================================
# Posts Operations
# =============================================================================

def load_posts() -> pd.DataFrame:
    """
    Load all post ideas from CSV.

    Returns:
        pd.DataFrame: DataFrame with columns: id, title, description, topic, subtopic, effort, status
    """
    posts_path = DATA_DIR / "posts.csv"
    return pd.read_csv(posts_path)


def save_posts(posts_df: pd.DataFrame) -> bool:
    """
    Save posts DataFrame to CSV.

    Args:
        posts_df: DataFrame with post data.

    Returns:
        bool: True if save was successful.
    """
    posts_path = DATA_DIR / "posts.csv"

    try:
        posts_df.to_csv(posts_path, index=False)
        return True
    except Exception as e:
        print(f"Error saving posts: {e}")
        return False


def get_posts_by_subtopic(subtopic: str) -> pd.DataFrame:
    """
    Get all posts for a specific subtopic.

    Args:
        subtopic: The subtopic name to filter by.

    Returns:
        pd.DataFrame: Filtered posts for that subtopic.
    """
    posts_df = load_posts()
    return posts_df[posts_df['subtopic'] == subtopic].copy()


def get_posts_by_topic(topic: str) -> pd.DataFrame:
    """
    Get all posts for a specific topic.

    Args:
        topic: The topic name to filter by.

    Returns:
        pd.DataFrame: Filtered posts for that topic.
    """
    posts_df = load_posts()
    return posts_df[posts_df['topic'] == topic].copy()


def get_posts_by_effort(min_effort: int = 1, max_effort: int = 5) -> pd.DataFrame:
    """
    Filter posts by effort level range.

    Args:
        min_effort: Minimum effort level (1-5, inclusive).
        max_effort: Maximum effort level (1-5, inclusive).

    Returns:
        pd.DataFrame: Posts within the effort range.
    """
    posts_df = load_posts()
    filtered = posts_df[
        (posts_df['effort'] >= min_effort) &
        (posts_df['effort'] <= max_effort)
    ]
    return filtered.copy()


def get_posts_filtered(
    subtopic: str = None,
    topic: str = None,
    min_effort: int = 1,
    max_effort: int = 5,
    status: str = None
) -> pd.DataFrame:
    """
    Get posts with multiple filters applied.

    Args:
        subtopic: Optional subtopic filter.
        topic: Optional topic filter.
        min_effort: Minimum effort level.
        max_effort: Maximum effort level.
        status: Optional status filter (draft/posted/archived).

    Returns:
        pd.DataFrame: Filtered posts.
    """
    posts_df = load_posts()

    # Apply effort filter
    mask = (posts_df['effort'] >= min_effort) & (posts_df['effort'] <= max_effort)

    # Apply optional filters
    if subtopic:
        mask = mask & (posts_df['subtopic'] == subtopic)

    if topic:
        mask = mask & (posts_df['topic'] == topic)

    if status:
        mask = mask & (posts_df['status'] == status)

    return posts_df[mask].copy()


# =============================================================================
# Post History Operations
# =============================================================================

def load_post_history() -> pd.DataFrame:
    """
    Load post history from CSV.

    Returns:
        pd.DataFrame: History with columns: id, topic, subtopic, posted_date
    """
    history_path = DATA_DIR / "post_history.csv"

    # Handle empty file case
    if not os.path.exists(history_path):
        return pd.DataFrame(columns=['id', 'topic', 'subtopic', 'posted_date'])

    history_df = pd.read_csv(history_path)

    # Convert posted_date to datetime for proper sorting
    if not history_df.empty:
        history_df['posted_date'] = pd.to_datetime(history_df['posted_date'])

    return history_df


def save_post_history(history_df: pd.DataFrame) -> bool:
    """
    Save post history to CSV.

    Args:
        history_df: DataFrame with history data.

    Returns:
        bool: True if save was successful.
    """
    history_path = DATA_DIR / "post_history.csv"

    try:
        # Convert datetime back to string for CSV storage
        history_copy = history_df.copy()
        if 'posted_date' in history_copy.columns and not history_copy.empty:
            history_copy['posted_date'] = pd.to_datetime(history_copy['posted_date']).dt.strftime('%Y-%m-%d')

        history_copy.to_csv(history_path, index=False)
        return True
    except Exception as e:
        print(f"Error saving post history: {e}")
        return False


def record_post(topic: str, subtopic: str, posted_date: str = None) -> tuple[bool, int]:
    """
    Record a new post to history.

    Args:
        topic: The topic that was posted.
        subtopic: The subtopic that was posted.
        posted_date: Optional date string (YYYY-MM-DD). Defaults to today.

    Returns:
        tuple: (success: bool, new_id: int)
    """
    history_df = load_post_history()

    # Generate new ID
    new_id = 1 if history_df.empty else history_df['id'].max() + 1

    # Use today if no date provided
    if posted_date is None:
        posted_date = datetime.now().strftime('%Y-%m-%d')

    # Create new row
    new_row = pd.DataFrame([{
        'id': new_id,
        'topic': topic,
        'subtopic': subtopic,
        'posted_date': posted_date
    }])

    # Append to history
    history_df = pd.concat([history_df, new_row], ignore_index=True)

    # Save
    success = save_post_history(history_df)

    return success, new_id


def get_recent_posts(n: int = 3) -> pd.DataFrame:
    """
    Get the n most recently posted items.

    Args:
        n: Number of recent posts to retrieve.

    Returns:
        pd.DataFrame: Most recent posts, sorted by date descending.
    """
    history_df = load_post_history()

    if history_df.empty:
        return history_df

    # Sort by date descending and take top n
    sorted_df = history_df.sort_values('posted_date', ascending=False)
    return sorted_df.head(n).copy()


def get_recent_topics(n: int = 3) -> list[str]:
    """
    Get list of n most recently posted topics.

    Args:
        n: Number of recent topics to retrieve.

    Returns:
        list: Topic names in order of recency (most recent first).
    """
    recent = get_recent_posts(n)
    return recent['topic'].tolist()


def get_recent_subtopics(n: int = 3) -> list[str]:
    """
    Get list of n most recently posted subtopics.

    Args:
        n: Number of recent subtopics to retrieve.

    Returns:
        list: Subtopic names in order of recency (most recent first).
    """
    recent = get_recent_posts(n)
    return recent['subtopic'].tolist()


# =============================================================================
# Standalone Test Section
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Testing selector_db.py")
    print("=" * 60)

    # Test probability tree
    print("\n--- Probability Tree ---")
    tree = load_probability_tree()
    topics = get_all_topics()
    print(f"Topics: {topics}")

    # Show subtopics for first topic
    first_topic = topics[0]
    subtopics = get_subtopics_for_topic(first_topic)
    print(f"Subtopics for '{first_topic}': {subtopics}")

    # Test posts
    print("\n--- Posts ---")
    posts_df = load_posts()
    print(f"Total posts: {len(posts_df)}")
    print(f"Columns: {list(posts_df.columns)}")
    print(f"\nFirst 3 posts:")
    print(posts_df.head(3)[['id', 'title', 'topic', 'subtopic', 'effort']])

    # Test filtering
    print("\n--- Filtering ---")
    effort_filtered = get_posts_by_effort(1, 2)
    print(f"Posts with effort 1-2: {len(effort_filtered)}")

    subtopic_posts = get_posts_by_subtopic('contemporary')
    print(f"Posts for 'contemporary': {len(subtopic_posts)}")

    # Test history
    print("\n--- Post History ---")
    history_df = load_post_history()
    print(f"History entries: {len(history_df)}")
    print(history_df)

    recent_topics = get_recent_topics(3)
    print(f"\nRecent topics: {recent_topics}")

    recent_subtopics = get_recent_subtopics(3)
    print(f"Recent subtopics: {recent_subtopics}")

    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)
