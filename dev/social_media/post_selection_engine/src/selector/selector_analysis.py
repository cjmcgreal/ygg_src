"""
Analysis layer for the post selection engine.

Contains data analysis and statistics functions:
- Topic/subtopic posting statistics
- Effort distribution analysis
- Posting trends and patterns
"""

from datetime import datetime, timedelta

import pandas as pd


# =============================================================================
# Topic Statistics
# =============================================================================

def calculate_topic_statistics(history_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate posting statistics per topic.

    Args:
        history_df: Post history DataFrame with columns: topic, subtopic, posted_date

    Returns:
        pd.DataFrame: Statistics with columns:
            - topic: Topic name
            - post_count: Number of posts for this topic
            - percentage: Percentage of total posts
            - last_posted: Date of most recent post
            - days_since_last: Days since last post (None if never posted)
    """
    if history_df.empty:
        return pd.DataFrame(columns=['topic', 'post_count', 'percentage', 'last_posted', 'days_since_last'])

    # Ensure posted_date is datetime
    history_df = history_df.copy()
    history_df['posted_date'] = pd.to_datetime(history_df['posted_date'])

    today = datetime.now().date()

    # Group by topic
    stats = history_df.groupby('topic').agg({
        'id': 'count',
        'posted_date': 'max'
    }).reset_index()

    stats.columns = ['topic', 'post_count', 'last_posted']

    # Calculate percentage
    total_posts = stats['post_count'].sum()
    stats['percentage'] = (stats['post_count'] / total_posts * 100).round(1)

    # Calculate days since last post
    stats['days_since_last'] = stats['last_posted'].apply(
        lambda x: (today - x.date()).days if pd.notna(x) else None
    )

    # Format last_posted as string
    stats['last_posted'] = stats['last_posted'].dt.strftime('%Y-%m-%d')

    # Sort by post count descending
    stats = stats.sort_values('post_count', ascending=False)

    return stats


def calculate_subtopic_statistics(history_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate posting statistics per subtopic.

    Args:
        history_df: Post history DataFrame.

    Returns:
        pd.DataFrame: Statistics with columns:
            - topic: Parent topic
            - subtopic: Subtopic name
            - post_count: Number of posts
            - last_posted: Date of most recent post
            - days_since_last: Days since last post
    """
    if history_df.empty:
        return pd.DataFrame(columns=['topic', 'subtopic', 'post_count', 'last_posted', 'days_since_last'])

    history_df = history_df.copy()
    history_df['posted_date'] = pd.to_datetime(history_df['posted_date'])

    today = datetime.now().date()

    # Group by topic and subtopic
    stats = history_df.groupby(['topic', 'subtopic']).agg({
        'id': 'count',
        'posted_date': 'max'
    }).reset_index()

    stats.columns = ['topic', 'subtopic', 'post_count', 'last_posted']

    # Calculate days since last post
    stats['days_since_last'] = stats['last_posted'].apply(
        lambda x: (today - x.date()).days if pd.notna(x) else None
    )

    # Format last_posted as string
    stats['last_posted'] = stats['last_posted'].dt.strftime('%Y-%m-%d')

    # Sort by topic then by days since last (prioritize topics not posted recently)
    stats = stats.sort_values(['topic', 'days_since_last'], ascending=[True, False])

    return stats


# =============================================================================
# Effort Analysis
# =============================================================================

def analyze_effort_distribution(posts_df: pd.DataFrame) -> dict:
    """
    Analyze effort distribution across all posts.

    Args:
        posts_df: Posts DataFrame with 'effort' column.

    Returns:
        dict: Analysis results with:
            - count_by_level: Dict of effort level -> count
            - percentage_by_level: Dict of effort level -> percentage
            - average_effort: Average effort across all posts
            - effort_by_topic: Dict of topic -> average effort
    """
    if posts_df.empty:
        return {
            'count_by_level': {},
            'percentage_by_level': {},
            'average_effort': 0,
            'effort_by_topic': {}
        }

    # Count by effort level
    effort_counts = posts_df['effort'].value_counts().sort_index()
    count_by_level = effort_counts.to_dict()

    # Percentage by level
    total = len(posts_df)
    percentage_by_level = {
        level: round(count / total * 100, 1)
        for level, count in count_by_level.items()
    }

    # Average effort overall
    average_effort = round(posts_df['effort'].mean(), 2)

    # Average effort by topic
    effort_by_topic = posts_df.groupby('topic')['effort'].mean().round(2).to_dict()

    return {
        'count_by_level': count_by_level,
        'percentage_by_level': percentage_by_level,
        'average_effort': average_effort,
        'effort_by_topic': effort_by_topic
    }


def get_effort_summary_df(posts_df: pd.DataFrame) -> pd.DataFrame:
    """
    Get effort distribution as a DataFrame for display.

    Args:
        posts_df: Posts DataFrame.

    Returns:
        pd.DataFrame: Effort level summary with count and percentage.
    """
    analysis = analyze_effort_distribution(posts_df)

    rows = []
    for level in range(1, 6):
        rows.append({
            'effort_level': level,
            'count': analysis['count_by_level'].get(level, 0),
            'percentage': analysis['percentage_by_level'].get(level, 0)
        })

    return pd.DataFrame(rows)


# =============================================================================
# Posting Trends
# =============================================================================

def get_posting_trends(history_df: pd.DataFrame, days: int = 30) -> pd.DataFrame:
    """
    Get posting frequency trends over the last N days.

    Args:
        history_df: Post history DataFrame.
        days: Number of days to analyze.

    Returns:
        pd.DataFrame: Daily posting counts with columns: date, count
    """
    if history_df.empty:
        return pd.DataFrame(columns=['date', 'count'])

    history_df = history_df.copy()
    history_df['posted_date'] = pd.to_datetime(history_df['posted_date'])

    # Get date range
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)

    # Filter to date range
    mask = (history_df['posted_date'].dt.date >= start_date) & \
           (history_df['posted_date'].dt.date <= end_date)
    filtered = history_df[mask]

    # Count by date
    daily_counts = filtered.groupby(filtered['posted_date'].dt.date).size()

    # Create full date range DataFrame (include days with 0 posts)
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    result = pd.DataFrame({'date': date_range.date})
    result['count'] = result['date'].map(daily_counts).fillna(0).astype(int)

    return result


def get_topic_frequency_df(history_df: pd.DataFrame) -> pd.DataFrame:
    """
    Get topic posting frequency for chart display.

    Args:
        history_df: Post history DataFrame.

    Returns:
        pd.DataFrame: Topics with their post counts, sorted by count.
    """
    if history_df.empty:
        return pd.DataFrame(columns=['topic', 'count'])

    counts = history_df.groupby('topic').size().reset_index(name='count')
    return counts.sort_values('count', ascending=False)


# =============================================================================
# Coverage Analysis
# =============================================================================

def find_underrepresented_subtopics(
    tree: dict,
    history_df: pd.DataFrame,
    threshold_pct: float = 0.5
) -> list[dict]:
    """
    Find subtopics that have been posted less than expected based on probability.

    Args:
        tree: The probability tree.
        history_df: Post history DataFrame.
        threshold_pct: Threshold as a percentage of expected (0.5 = less than half expected).

    Returns:
        list: List of dicts with topic, subtopic, expected_pct, actual_pct, ratio
    """
    if history_df.empty:
        # Return all subtopics as underrepresented
        results = []
        for topic, data in tree['topics'].items():
            topic_prob = data['probability']
            for subtopic, sub_prob in data['subtopics'].items():
                expected = topic_prob * sub_prob * 100
                results.append({
                    'topic': topic,
                    'subtopic': subtopic,
                    'expected_pct': round(expected, 2),
                    'actual_pct': 0,
                    'ratio': 0
                })
        return results

    total_posts = len(history_df)

    # Calculate actual percentages
    subtopic_counts = history_df.groupby(['topic', 'subtopic']).size()

    results = []

    for topic, data in tree['topics'].items():
        topic_prob = data['probability']
        for subtopic, sub_prob in data['subtopics'].items():
            # Expected percentage based on probability
            expected_pct = topic_prob * sub_prob * 100

            # Actual count and percentage
            try:
                actual_count = subtopic_counts.loc[(topic, subtopic)]
            except KeyError:
                actual_count = 0

            actual_pct = (actual_count / total_posts * 100) if total_posts > 0 else 0

            # Calculate ratio (actual / expected)
            ratio = actual_pct / expected_pct if expected_pct > 0 else 0

            # Only include if under threshold
            if ratio < threshold_pct:
                results.append({
                    'topic': topic,
                    'subtopic': subtopic,
                    'expected_pct': round(expected_pct, 2),
                    'actual_pct': round(actual_pct, 2),
                    'ratio': round(ratio, 2)
                })

    # Sort by ratio (most underrepresented first)
    results.sort(key=lambda x: x['ratio'])

    return results


def get_coverage_summary(tree: dict, history_df: pd.DataFrame) -> dict:
    """
    Get summary of topic/subtopic coverage.

    Args:
        tree: The probability tree.
        history_df: Post history DataFrame.

    Returns:
        dict: Summary with total counts and coverage percentages.
    """
    total_topics = len(tree['topics'])
    total_subtopics = sum(len(data['subtopics']) for data in tree['topics'].values())

    if history_df.empty:
        return {
            'total_topics': total_topics,
            'topics_posted': 0,
            'topics_coverage_pct': 0,
            'total_subtopics': total_subtopics,
            'subtopics_posted': 0,
            'subtopics_coverage_pct': 0
        }

    topics_posted = history_df['topic'].nunique()
    subtopics_posted = history_df.groupby(['topic', 'subtopic']).ngroups

    return {
        'total_topics': total_topics,
        'topics_posted': topics_posted,
        'topics_coverage_pct': round(topics_posted / total_topics * 100, 1),
        'total_subtopics': total_subtopics,
        'subtopics_posted': subtopics_posted,
        'subtopics_coverage_pct': round(subtopics_posted / total_subtopics * 100, 1)
    }


# =============================================================================
# Standalone Test Section
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Testing selector_analysis.py")
    print("=" * 60)

    # Create sample data
    sample_history = pd.DataFrame([
        {'id': 1, 'topic': 'dance', 'subtopic': 'contemporary', 'posted_date': '2024-11-25'},
        {'id': 2, 'topic': 'music', 'subtopic': 'guitar_practice', 'posted_date': '2024-11-22'},
        {'id': 3, 'topic': 'travel', 'subtopic': 'destinations', 'posted_date': '2024-11-20'},
        {'id': 4, 'topic': 'dance', 'subtopic': 'salsa', 'posted_date': '2024-11-18'},
        {'id': 5, 'topic': 'music', 'subtopic': 'concerts', 'posted_date': '2024-11-15'},
    ])

    sample_posts = pd.DataFrame([
        {'id': 1, 'topic': 'dance', 'subtopic': 'contemporary', 'effort': 3},
        {'id': 2, 'topic': 'dance', 'subtopic': 'salsa', 'effort': 2},
        {'id': 3, 'topic': 'music', 'subtopic': 'guitar_practice', 'effort': 4},
        {'id': 4, 'topic': 'music', 'subtopic': 'concerts', 'effort': 2},
        {'id': 5, 'topic': 'travel', 'subtopic': 'destinations', 'effort': 5},
    ])

    # Test topic statistics
    print("\n--- Topic Statistics ---")
    topic_stats = calculate_topic_statistics(sample_history)
    print(topic_stats)

    # Test subtopic statistics
    print("\n--- Subtopic Statistics ---")
    subtopic_stats = calculate_subtopic_statistics(sample_history)
    print(subtopic_stats)

    # Test effort analysis
    print("\n--- Effort Distribution ---")
    effort_analysis = analyze_effort_distribution(sample_posts)
    print(f"Average effort: {effort_analysis['average_effort']}")
    print(f"Count by level: {effort_analysis['count_by_level']}")
    print(f"Effort by topic: {effort_analysis['effort_by_topic']}")

    # Test posting trends
    print("\n--- Posting Trends (last 30 days) ---")
    trends = get_posting_trends(sample_history, days=30)
    posts_in_range = trends['count'].sum()
    print(f"Posts in last 30 days: {posts_in_range}")

    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)
