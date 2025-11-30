"""
Business logic for the post selection engine.

Contains:
- Probability tree validation
- Recency penalty calculations
- Probability redistribution
- Weighted random selection
- Two-level hierarchical draw algorithm
"""

import random
from typing import Optional


# Penalty multipliers for recency (position 0 = most recent)
# 100% penalty means probability becomes 0
# 50% penalty means probability is halved
# 25% penalty means probability is reduced by 25%
PENALTY_MULTIPLIERS = [0.0, 0.5, 0.75]  # [100% penalty, 50% penalty, 25% penalty]


# =============================================================================
# Validation Functions
# =============================================================================

def validate_probability_tree(tree: dict) -> tuple[bool, str]:
    """
    Validate the structure and constraints of a probability tree.

    Checks:
    - All topic probabilities sum to 1.0 (within tolerance)
    - Each topic's subtopic probabilities sum to 1.0
    - All probabilities are between 0 and 1

    Args:
        tree: The probability tree dictionary.

    Returns:
        tuple: (is_valid: bool, message: str)
    """
    tolerance = 0.001  # Allow small floating point errors

    if "topics" not in tree:
        return False, "Missing 'topics' key in tree"

    topics = tree["topics"]

    if not topics:
        return False, "No topics defined"

    # Check topic probabilities sum to 1
    topic_sum = sum(t["probability"] for t in topics.values())
    if abs(topic_sum - 1.0) > tolerance:
        return False, f"Topic probabilities sum to {topic_sum:.4f}, should be 1.0"

    # Check each topic
    for topic_name, topic_data in topics.items():
        # Check probability range
        prob = topic_data.get("probability", 0)
        if prob < 0 or prob > 1:
            return False, f"Topic '{topic_name}' has invalid probability: {prob}"

        # Check subtopics exist
        if "subtopics" not in topic_data:
            return False, f"Topic '{topic_name}' has no subtopics"

        subtopics = topic_data["subtopics"]
        if not subtopics:
            return False, f"Topic '{topic_name}' has empty subtopics"

        # Check subtopic probabilities sum to 1
        subtopic_sum = sum(subtopics.values())
        if abs(subtopic_sum - 1.0) > tolerance:
            return False, f"Subtopics for '{topic_name}' sum to {subtopic_sum:.4f}, should be 1.0"

        # Check each subtopic probability range
        for sub_name, sub_prob in subtopics.items():
            if sub_prob < 0 or sub_prob > 1:
                return False, f"Subtopic '{sub_name}' in '{topic_name}' has invalid probability: {sub_prob}"

    return True, "Probability tree is valid"


def validate_effort_level(effort: int) -> tuple[bool, str]:
    """
    Validate effort level is within valid range.

    Args:
        effort: The effort level to validate.

    Returns:
        tuple: (is_valid: bool, message: str)
    """
    if not isinstance(effort, int):
        return False, f"Effort must be an integer, got {type(effort).__name__}"

    if effort < 1 or effort > 5:
        return False, f"Effort must be between 1 and 5, got {effort}"

    return True, "Valid effort level"


# =============================================================================
# Penalty Application
# =============================================================================

def apply_recency_penalties(
    probabilities: dict[str, float],
    recent_items: list[str]
) -> dict[str, float]:
    """
    Apply recency penalties to a probability distribution.

    Penalties:
    - Most recent (index 0): 100% penalty -> probability becomes 0
    - Second recent (index 1): 50% penalty -> probability * 0.5
    - Third recent (index 2): 25% penalty -> probability * 0.75

    The probability removed from penalized items is redistributed
    proportionally to non-penalized items.

    Args:
        probabilities: Dictionary mapping item names to their base probabilities.
        recent_items: List of recently selected items (most recent first).

    Returns:
        dict: Adjusted probabilities after penalties and redistribution.
    """
    if not probabilities:
        return {}

    # Start with a copy of original probabilities
    adjusted = probabilities.copy()
    total_penalty = 0.0

    # Apply penalties to recent items
    for i, item in enumerate(recent_items[:3]):
        if item in adjusted:
            original = adjusted[item]
            multiplier = PENALTY_MULTIPLIERS[i]
            adjusted[item] = original * multiplier
            penalty_amount = original - adjusted[item]
            total_penalty += penalty_amount

    # Find non-penalized items (targets for redistribution)
    penalized_items = set(recent_items[:3])
    targets = {k: v for k, v in adjusted.items()
               if k not in penalized_items and v > 0}

    # Handle edge case: all items are penalized
    if not targets:
        # Normalize remaining probabilities so they still sum to 1
        total = sum(adjusted.values())
        if total > 0:
            return {k: v / total for k, v in adjusted.items()}
        return adjusted

    # Redistribute penalty amount proportionally to targets
    target_sum = sum(targets.values())
    for item in targets:
        share = targets[item] / target_sum
        adjusted[item] += total_penalty * share

    return adjusted


def get_topic_probabilities(tree: dict) -> dict[str, float]:
    """
    Extract topic probabilities from the tree.

    Args:
        tree: The probability tree.

    Returns:
        dict: Mapping of topic name to probability.
    """
    return {name: data["probability"] for name, data in tree["topics"].items()}


def get_subtopic_probabilities(tree: dict, topic: str) -> dict[str, float]:
    """
    Extract subtopic probabilities for a given topic.

    Args:
        tree: The probability tree.
        topic: The topic name.

    Returns:
        dict: Mapping of subtopic name to probability.
    """
    if topic not in tree["topics"]:
        return {}

    return tree["topics"][topic]["subtopics"].copy()


def calculate_adjusted_topic_probabilities(
    tree: dict,
    recent_topics: list[str]
) -> dict[str, float]:
    """
    Calculate topic probabilities after applying recency penalties.

    Args:
        tree: The probability tree.
        recent_topics: List of recently posted topics (most recent first).

    Returns:
        dict: Adjusted topic probabilities.
    """
    base_probs = get_topic_probabilities(tree)
    return apply_recency_penalties(base_probs, recent_topics)


def calculate_adjusted_subtopic_probabilities(
    tree: dict,
    selected_topic: str,
    recent_subtopics: list[str]
) -> dict[str, float]:
    """
    Calculate subtopic probabilities for a topic after applying penalties.

    Args:
        tree: The probability tree.
        selected_topic: The topic that was selected.
        recent_subtopics: List of recently posted subtopics (most recent first).

    Returns:
        dict: Adjusted subtopic probabilities.
    """
    base_probs = get_subtopic_probabilities(tree, selected_topic)
    return apply_recency_penalties(base_probs, recent_subtopics)


# =============================================================================
# Selection Functions
# =============================================================================

def weighted_random_choice(probabilities: dict[str, float]) -> Optional[str]:
    """
    Select an item based on probability distribution.

    Uses random.choices() for weighted random selection.

    Args:
        probabilities: Dictionary mapping item names to probabilities.

    Returns:
        str: Selected item name, or None if probabilities are empty/invalid.
    """
    if not probabilities:
        return None

    # Filter out zero probabilities
    valid_probs = {k: v for k, v in probabilities.items() if v > 0}

    if not valid_probs:
        return None

    items = list(valid_probs.keys())
    weights = list(valid_probs.values())

    # Use random.choices which handles weighted selection
    selected = random.choices(items, weights=weights, k=1)[0]

    return selected


def run_hierarchical_draw(
    tree: dict,
    recent_topics: list[str],
    recent_subtopics: list[str]
) -> tuple[str, str, dict]:
    """
    Execute the two-level probabilistic draw with recency penalties.

    This is the main draw algorithm:
    1. Apply penalties to topic probabilities
    2. Select a topic using adjusted probabilities
    3. Apply penalties to that topic's subtopic probabilities
    4. Select a subtopic using adjusted probabilities

    Args:
        tree: The probability tree.
        recent_topics: List of recently posted topics (most recent first).
        recent_subtopics: List of recently posted subtopics (most recent first).

    Returns:
        tuple: (selected_topic, selected_subtopic, debug_info)
               debug_info contains adjusted probabilities for transparency.
    """
    # Step 1: Calculate adjusted topic probabilities
    adjusted_topic_probs = calculate_adjusted_topic_probabilities(tree, recent_topics)

    # Step 2: Select topic
    selected_topic = weighted_random_choice(adjusted_topic_probs)

    if not selected_topic:
        return None, None, {"error": "Could not select topic"}

    # Step 3: Calculate adjusted subtopic probabilities for selected topic
    adjusted_subtopic_probs = calculate_adjusted_subtopic_probabilities(
        tree, selected_topic, recent_subtopics
    )

    # Step 4: Select subtopic
    selected_subtopic = weighted_random_choice(adjusted_subtopic_probs)

    if not selected_subtopic:
        return selected_topic, None, {
            "error": "Could not select subtopic",
            "adjusted_topic_probs": adjusted_topic_probs
        }

    # Build debug info for transparency
    debug_info = {
        "adjusted_topic_probs": adjusted_topic_probs,
        "adjusted_subtopic_probs": adjusted_subtopic_probs,
        "recent_topics": recent_topics,
        "recent_subtopics": recent_subtopics
    }

    return selected_topic, selected_subtopic, debug_info


# =============================================================================
# Utility Functions
# =============================================================================

def normalize_probabilities(probabilities: dict[str, float]) -> dict[str, float]:
    """
    Normalize probabilities so they sum to 1.0.

    Args:
        probabilities: Dictionary of probabilities.

    Returns:
        dict: Normalized probabilities summing to 1.0.
    """
    total = sum(probabilities.values())

    if total == 0:
        # Equal distribution if all are zero
        n = len(probabilities)
        return {k: 1.0 / n for k in probabilities}

    return {k: v / total for k, v in probabilities.items()}


def update_probability_tree(
    tree: dict,
    topic: str,
    new_topic_prob: Optional[float] = None,
    subtopic_probs: Optional[dict[str, float]] = None
) -> tuple[bool, str]:
    """
    Update probabilities in the tree for a specific topic.

    Note: After updating, you must manually normalize other topics
    to ensure they sum to 1.0.

    Args:
        tree: The probability tree (modified in place).
        topic: Topic to update.
        new_topic_prob: Optional new probability for the topic.
        subtopic_probs: Optional new subtopic probabilities dict.

    Returns:
        tuple: (success: bool, message: str)
    """
    if topic not in tree["topics"]:
        return False, f"Topic '{topic}' not found in tree"

    if new_topic_prob is not None:
        if new_topic_prob < 0 or new_topic_prob > 1:
            return False, f"Invalid topic probability: {new_topic_prob}"
        tree["topics"][topic]["probability"] = new_topic_prob

    if subtopic_probs is not None:
        # Validate subtopic probabilities
        if abs(sum(subtopic_probs.values()) - 1.0) > 0.001:
            return False, "Subtopic probabilities must sum to 1.0"

        tree["topics"][topic]["subtopics"] = subtopic_probs

    return True, "Update successful"


# =============================================================================
# Standalone Test Section
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Testing selector_logic.py")
    print("=" * 60)

    # Test penalty application
    print("\n--- Testing Recency Penalties ---")

    test_probs = {
        "A": 0.25,
        "B": 0.25,
        "C": 0.25,
        "D": 0.25
    }

    print(f"Original probabilities: {test_probs}")
    print(f"Sum: {sum(test_probs.values()):.2f}")

    # Test with one recent item (100% penalty)
    recent = ["A"]
    adjusted = apply_recency_penalties(test_probs, recent)
    print(f"\nAfter penalizing 'A' (100%): {adjusted}")
    print(f"Sum: {sum(adjusted.values()):.4f}")

    # Test with three recent items
    recent = ["A", "B", "C"]
    adjusted = apply_recency_penalties(test_probs, recent)
    print(f"\nAfter penalizing A(100%), B(50%), C(25%): {adjusted}")
    print(f"Sum: {sum(adjusted.values()):.4f}")

    # Test hierarchical draw
    print("\n--- Testing Hierarchical Draw ---")

    test_tree = {
        "topics": {
            "topic1": {
                "probability": 0.5,
                "subtopics": {
                    "sub1a": 0.5,
                    "sub1b": 0.5
                }
            },
            "topic2": {
                "probability": 0.5,
                "subtopics": {
                    "sub2a": 0.5,
                    "sub2b": 0.5
                }
            }
        }
    }

    # Validate tree
    is_valid, msg = validate_probability_tree(test_tree)
    print(f"Tree validation: {is_valid} - {msg}")

    # Run some draws
    print("\nRunning 10 draws with no history:")
    for i in range(10):
        topic, subtopic, debug = run_hierarchical_draw(test_tree, [], [])
        print(f"  Draw {i+1}: {topic} -> {subtopic}")

    # Run draws with recent history
    print("\nRunning 5 draws with topic1, sub1a as most recent:")
    for i in range(5):
        topic, subtopic, debug = run_hierarchical_draw(
            test_tree,
            ["topic1"],
            ["sub1a"]
        )
        print(f"  Draw {i+1}: {topic} -> {subtopic}")

    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)
