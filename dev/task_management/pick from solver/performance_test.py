"""
Performance Test for Task Selection Algorithms

Tests the performance of all three solver algorithms with larger datasets.
"""

import sys
sys.path.insert(0, 'src')

import pandas as pd
import time
from task_selection.task_selection_analysis import greedy_solver, weighted_solver, knapsack_solver


def run_performance_test(num_tasks):
    """
    Run performance test with specified number of tasks.

    Args:
        num_tasks (int): Number of tasks to generate for testing
    """
    # Create test tasks
    tasks_data = []
    domains = ['backend', 'frontend', 'design', 'devops', 'testing']
    for i in range(1, num_tasks + 1):
        tasks_data.append({
            'id': i,
            'title': f'Task {i}',
            'description': f'Description for task {i}',
            'domain': domains[i % 5],
            'project_parent': f'project_{i % 10}',
            'effort': (i % 10) + 1,  # 1-10 story points
            'value': (i % 9) + 2,    # 2-10 value
            'priority': (i % 5) + 1  # 1-5 priority
        })

    tasks_df = pd.DataFrame(tasks_data)
    available_time = num_tasks * 2.0  # Generous time allocation
    domain_prefs = {
        'backend': 30,
        'frontend': 25,
        'design': 20,
        'devops': 15,
        'testing': 10
    }

    print(f'\nPerformance Test: {num_tasks} Tasks')
    print('=' * 80)
    print(f'Available time: {available_time}sp')
    print(f'Number of tasks: {len(tasks_df)}')
    print()

    # Test Greedy
    start = time.time()
    selected, explanation, metrics = greedy_solver(tasks_df, available_time, domain_prefs)
    greedy_time = (time.time() - start) * 1000
    print(f'Greedy Solver:    {greedy_time:7.2f}ms - Selected {len(selected):2d} tasks')

    # Test Weighted
    start = time.time()
    selected, explanation, metrics = weighted_solver(tasks_df, available_time, domain_prefs)
    weighted_time = (time.time() - start) * 1000
    print(f'Weighted Solver:  {weighted_time:7.2f}ms - Selected {len(selected):2d} tasks')

    # Test Knapsack
    start = time.time()
    selected, explanation, metrics = knapsack_solver(tasks_df, available_time, domain_prefs)
    knapsack_time = (time.time() - start) * 1000
    print(f'Knapsack Solver:  {knapsack_time:7.2f}ms - Selected {len(selected):2d} tasks')

    print()
    max_time = max(greedy_time, weighted_time, knapsack_time)
    print(f'Maximum execution time: {max_time:.2f}ms')

    return max_time


if __name__ == "__main__":
    print('=' * 80)
    print('TASK SELECTION ALGORITHM PERFORMANCE TESTS')
    print('=' * 80)

    # Test with different dataset sizes
    test_sizes = [10, 25, 50, 100]
    results = {}

    for size in test_sizes:
        max_time = run_performance_test(size)
        results[size] = max_time

    # Summary
    print('\n' + '=' * 80)
    print('PERFORMANCE SUMMARY')
    print('=' * 80)
    print(f'{"Tasks":>10} {"Max Time (ms)":>15} {"Status":>15}')
    print('-' * 80)

    for size, time_ms in results.items():
        status = 'PASS' if time_ms < 5000 else 'FAIL'
        print(f'{size:>10} {time_ms:>15.2f} {status:>15}')

    print()
    print('Performance requirement: < 5000ms (5 seconds) for 50 tasks')

    # Check 50-task requirement
    if 50 in results:
        if results[50] < 5000:
            print(f'Result: PASS - 50 tasks completed in {results[50]:.2f}ms')
        else:
            print(f'Result: FAIL - 50 tasks took {results[50]:.2f}ms (exceeds 5000ms)')
