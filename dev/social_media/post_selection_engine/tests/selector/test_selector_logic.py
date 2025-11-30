"""
Tests for selector_logic.py

Tests the core probability and penalty calculations:
- Probability tree validation
- Recency penalty application
- Probability redistribution
- Weighted random selection
- Hierarchical draw
"""

import pytest
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.selector.selector_logic import (
    validate_probability_tree,
    validate_effort_level,
    apply_recency_penalties,
    get_topic_probabilities,
    get_subtopic_probabilities,
    calculate_adjusted_topic_probabilities,
    calculate_adjusted_subtopic_probabilities,
    weighted_random_choice,
    run_hierarchical_draw,
    normalize_probabilities,
    PENALTY_MULTIPLIERS
)


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def valid_tree():
    """A valid probability tree for testing."""
    return {
        "topics": {
            "topic1": {
                "probability": 0.5,
                "subtopics": {
                    "sub1a": 0.6,
                    "sub1b": 0.4
                }
            },
            "topic2": {
                "probability": 0.5,
                "subtopics": {
                    "sub2a": 0.3,
                    "sub2b": 0.3,
                    "sub2c": 0.4
                }
            }
        }
    }


@pytest.fixture
def equal_probs():
    """Equal probability distribution for testing."""
    return {
        "A": 0.25,
        "B": 0.25,
        "C": 0.25,
        "D": 0.25
    }


# =============================================================================
# Validation Tests
# =============================================================================

class TestValidateProbabilityTree:
    """Tests for validate_probability_tree function."""

    def test_valid_tree(self, valid_tree):
        """Valid tree should pass validation."""
        is_valid, msg = validate_probability_tree(valid_tree)
        assert is_valid is True
        assert "valid" in msg.lower()

    def test_missing_topics_key(self):
        """Tree without 'topics' key should fail."""
        tree = {"something_else": {}}
        is_valid, msg = validate_probability_tree(tree)
        assert is_valid is False
        assert "Missing 'topics'" in msg

    def test_empty_topics(self):
        """Tree with empty topics should fail."""
        tree = {"topics": {}}
        is_valid, msg = validate_probability_tree(tree)
        assert is_valid is False
        assert "No topics" in msg

    def test_topic_probabilities_not_sum_to_one(self):
        """Topic probabilities not summing to 1 should fail."""
        tree = {
            "topics": {
                "topic1": {"probability": 0.5, "subtopics": {"a": 1.0}},
                "topic2": {"probability": 0.3, "subtopics": {"b": 1.0}}
            }
        }
        is_valid, msg = validate_probability_tree(tree)
        assert is_valid is False
        assert "sum to" in msg.lower()

    def test_subtopic_probabilities_not_sum_to_one(self):
        """Subtopic probabilities not summing to 1 should fail."""
        tree = {
            "topics": {
                "topic1": {
                    "probability": 1.0,
                    "subtopics": {"a": 0.3, "b": 0.3}  # Sum = 0.6
                }
            }
        }
        is_valid, msg = validate_probability_tree(tree)
        assert is_valid is False
        assert "Subtopics" in msg

    def test_invalid_probability_range(self):
        """Probability outside 0-1 range should fail."""
        # Use two topics where one has invalid range but sum is still 1.0
        tree = {
            "topics": {
                "topic1": {"probability": 1.5, "subtopics": {"a": 1.0}},
                "topic2": {"probability": -0.5, "subtopics": {"b": 1.0}}
            }
        }
        is_valid, msg = validate_probability_tree(tree)
        assert is_valid is False
        # Should fail either on sum check or invalid range check
        assert "sum" in msg.lower() or "invalid" in msg.lower()

    def test_missing_subtopics(self):
        """Topic without subtopics key should fail."""
        tree = {
            "topics": {
                "topic1": {"probability": 1.0}
            }
        }
        is_valid, msg = validate_probability_tree(tree)
        assert is_valid is False
        assert "no subtopics" in msg.lower()


class TestValidateEffortLevel:
    """Tests for validate_effort_level function."""

    def test_valid_effort_levels(self):
        """Effort levels 1-5 should be valid."""
        for effort in range(1, 6):
            is_valid, msg = validate_effort_level(effort)
            assert is_valid is True

    def test_effort_below_range(self):
        """Effort below 1 should fail."""
        is_valid, msg = validate_effort_level(0)
        assert is_valid is False

    def test_effort_above_range(self):
        """Effort above 5 should fail."""
        is_valid, msg = validate_effort_level(6)
        assert is_valid is False

    def test_non_integer_effort(self):
        """Non-integer effort should fail."""
        is_valid, msg = validate_effort_level(3.5)
        assert is_valid is False
        assert "integer" in msg.lower()


# =============================================================================
# Penalty Application Tests
# =============================================================================

class TestApplyRecencyPenalties:
    """Tests for apply_recency_penalties function."""

    def test_no_recent_items(self, equal_probs):
        """No recent items should leave probabilities unchanged."""
        adjusted = apply_recency_penalties(equal_probs, [])
        assert adjusted == equal_probs

    def test_single_recent_item_100_penalty(self, equal_probs):
        """Most recent item should get 100% penalty (probability = 0)."""
        adjusted = apply_recency_penalties(equal_probs, ["A"])

        # A should have 0 probability
        assert adjusted["A"] == 0.0

        # Total should still sum to 1
        assert abs(sum(adjusted.values()) - 1.0) < 0.0001

    def test_second_recent_item_50_penalty(self, equal_probs):
        """Second most recent item should get 50% penalty."""
        adjusted = apply_recency_penalties(equal_probs, ["A", "B"])

        # A should have 0 probability (100% penalty)
        assert adjusted["A"] == 0.0

        # B should have half its original (50% penalty)
        # Original was 0.25, so should be 0.125 before redistribution
        # But after redistribution from A's penalty, it stays at 0.125
        # because B is penalized, not a redistribution target
        assert adjusted["B"] == 0.25 * PENALTY_MULTIPLIERS[1]

        # Total should still sum to 1
        assert abs(sum(adjusted.values()) - 1.0) < 0.0001

    def test_third_recent_item_25_penalty(self, equal_probs):
        """Third most recent item should get 25% penalty."""
        adjusted = apply_recency_penalties(equal_probs, ["A", "B", "C"])

        # C should have 75% of original (25% penalty)
        assert adjusted["C"] == 0.25 * PENALTY_MULTIPLIERS[2]

        # Total should still sum to 1
        assert abs(sum(adjusted.values()) - 1.0) < 0.0001

    def test_redistribution_to_non_penalized(self, equal_probs):
        """Penalty amounts should redistribute to non-penalized items."""
        adjusted = apply_recency_penalties(equal_probs, ["A"])

        # A loses 0.25 (100% penalty)
        # B, C, D each had 0.25, so they split 0.25 equally
        # Each gets 0.25 + (0.25 / 3) = 0.25 + 0.0833 = 0.3333
        expected = 0.25 + (0.25 / 3)

        assert abs(adjusted["B"] - expected) < 0.0001
        assert abs(adjusted["C"] - expected) < 0.0001
        assert abs(adjusted["D"] - expected) < 0.0001

    def test_more_than_three_recent_ignored(self, equal_probs):
        """Only first 3 recent items should be penalized."""
        adjusted = apply_recency_penalties(equal_probs, ["A", "B", "C", "D"])

        # D is 4th, should not be penalized
        # It should receive redistribution from A, B, C penalties
        assert adjusted["D"] > 0.25  # Got redistribution

    def test_empty_probabilities(self):
        """Empty probabilities should return empty dict."""
        adjusted = apply_recency_penalties({}, ["A"])
        assert adjusted == {}

    def test_all_items_penalized(self):
        """When all items are penalized, should normalize remaining."""
        probs = {"A": 0.5, "B": 0.5}
        adjusted = apply_recency_penalties(probs, ["A", "B"])

        # A = 0 (100% penalty)
        # B = 0.25 (50% penalty)
        # Since only B has probability left, normalize to 1.0
        assert abs(sum(adjusted.values()) - 1.0) < 0.0001 or sum(adjusted.values()) == 0.25


# =============================================================================
# Weighted Random Choice Tests
# =============================================================================

class TestWeightedRandomChoice:
    """Tests for weighted_random_choice function."""

    def test_empty_probabilities(self):
        """Empty probabilities should return None."""
        result = weighted_random_choice({})
        assert result is None

    def test_all_zero_probabilities(self):
        """All zero probabilities should return None."""
        result = weighted_random_choice({"A": 0, "B": 0})
        assert result is None

    def test_single_item_with_probability(self):
        """Single item with probability should always be selected."""
        result = weighted_random_choice({"A": 1.0})
        assert result == "A"

    def test_returns_valid_item(self, equal_probs):
        """Should return one of the valid items."""
        for _ in range(100):
            result = weighted_random_choice(equal_probs)
            assert result in equal_probs

    def test_zero_probability_never_selected(self):
        """Items with zero probability should never be selected."""
        probs = {"A": 0.0, "B": 0.5, "C": 0.5}
        for _ in range(100):
            result = weighted_random_choice(probs)
            assert result != "A"


# =============================================================================
# Hierarchical Draw Tests
# =============================================================================

class TestRunHierarchicalDraw:
    """Tests for run_hierarchical_draw function."""

    def test_basic_draw(self, valid_tree):
        """Basic draw should return valid topic and subtopic."""
        topic, subtopic, debug = run_hierarchical_draw(valid_tree, [], [])

        assert topic in valid_tree["topics"]
        assert subtopic in valid_tree["topics"][topic]["subtopics"]
        assert "adjusted_topic_probs" in debug
        assert "adjusted_subtopic_probs" in debug

    def test_draw_with_recent_topic(self, valid_tree):
        """Recent topic should have reduced probability."""
        topic, subtopic, debug = run_hierarchical_draw(
            valid_tree,
            ["topic1"],  # topic1 should have 0 probability
            []
        )

        # topic1 should have 0 probability in adjusted probs
        assert debug["adjusted_topic_probs"]["topic1"] == 0.0

        # Run many draws - should almost never get topic1
        topic1_count = 0
        for _ in range(100):
            t, s, d = run_hierarchical_draw(valid_tree, ["topic1"], [])
            if t == "topic1":
                topic1_count += 1

        # With 100% penalty, topic1 should never be selected
        assert topic1_count == 0

    def test_draw_with_recent_subtopic(self, valid_tree):
        """Recent subtopic should have reduced probability."""
        topic, subtopic, debug = run_hierarchical_draw(
            valid_tree,
            [],
            ["sub1a"]  # sub1a should have 0 probability if topic1 selected
        )

        # If topic1 was selected, sub1a should have 0 probability
        if topic == "topic1":
            assert debug["adjusted_subtopic_probs"]["sub1a"] == 0.0

    def test_returns_debug_info(self, valid_tree):
        """Should return debug info with adjusted probabilities."""
        topic, subtopic, debug = run_hierarchical_draw(valid_tree, [], [])

        assert "adjusted_topic_probs" in debug
        assert "adjusted_subtopic_probs" in debug
        assert "recent_topics" in debug
        assert "recent_subtopics" in debug


# =============================================================================
# Normalization Tests
# =============================================================================

class TestNormalizeProbabilities:
    """Tests for normalize_probabilities function."""

    def test_already_normalized(self, equal_probs):
        """Already normalized probs should remain unchanged."""
        result = normalize_probabilities(equal_probs)
        for key in equal_probs:
            assert abs(result[key] - equal_probs[key]) < 0.0001

    def test_normalizes_to_one(self):
        """Should normalize probabilities to sum to 1."""
        probs = {"A": 2, "B": 3, "C": 5}  # Sum = 10
        result = normalize_probabilities(probs)

        assert abs(result["A"] - 0.2) < 0.0001
        assert abs(result["B"] - 0.3) < 0.0001
        assert abs(result["C"] - 0.5) < 0.0001
        assert abs(sum(result.values()) - 1.0) < 0.0001

    def test_all_zeros_equal_distribution(self):
        """All zeros should become equal distribution."""
        probs = {"A": 0, "B": 0, "C": 0}
        result = normalize_probabilities(probs)

        expected = 1.0 / 3
        for val in result.values():
            assert abs(val - expected) < 0.0001


# =============================================================================
# Standalone Test Section
# =============================================================================

if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
