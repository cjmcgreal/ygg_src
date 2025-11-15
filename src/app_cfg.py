"""
Application Configuration

Central configuration file for the Streamlit application.
Each domain can define its own configuration paths here.
"""

# Exercise domain configuration
EXERCISE_DATA_DIR = "domains/exercise/exercise_data"
EXERCISE_CSV_PATH = f"{EXERCISE_DATA_DIR}/exercises.csv"
EXERCISE_COMPLETED_CSV_PATH = f"{EXERCISE_DATA_DIR}/completed_exercises.csv"

# Task Management domain configuration
TASK_MANAGEMENT_DATA_DIR = "domains/task_management/task_management_data"
TASK_MANAGEMENT_CSV_PATH = f"{TASK_MANAGEMENT_DATA_DIR}/tasks.csv"

# Travel domain configuration
TRAVEL_DATA_DIR = "domains/travel/travel_data"
TRAVEL_CSV_PATH = f"{TRAVEL_DATA_DIR}/trips.csv"

# Finance domain configuration
FINANCE_DATA_DIR = "domains/finance/finance_data"
FINANCE_CSV_PATH = f"{FINANCE_DATA_DIR}/transactions.csv"

# Trees domain configuration
TREES_DATA_DIR = "domains/trees/trees_data"
TREES_CSV_PATH = f"{TREES_DATA_DIR}/tree_data.csv"


if __name__ == "__main__":
    # Standalone test - show all configured paths
    print("Application Configuration - Standalone Test")
    print("=" * 50)
    print("\nConfigured data paths:")
    print(f"\nExercise:")
    print(f"  - Data dir: {EXERCISE_DATA_DIR}")
    print(f"  - CSV path: {EXERCISE_CSV_PATH}")
    print(f"  - Completed CSV: {EXERCISE_COMPLETED_CSV_PATH}")
    print(f"\nTask Management:")
    print(f"  - Data dir: {TASK_MANAGEMENT_DATA_DIR}")
    print(f"  - CSV path: {TASK_MANAGEMENT_CSV_PATH}")
    print(f"\nTravel:")
    print(f"  - Data dir: {TRAVEL_DATA_DIR}")
    print(f"  - CSV path: {TRAVEL_CSV_PATH}")
    print(f"\nFinance:")
    print(f"  - Data dir: {FINANCE_DATA_DIR}")
    print(f"  - CSV path: {FINANCE_CSV_PATH}")
    print(f"\nTrees:")
    print(f"  - Data dir: {TREES_DATA_DIR}")
    print(f"  - CSV path: {TREES_CSV_PATH}")