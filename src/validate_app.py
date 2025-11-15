#!/usr/bin/env python
"""
Validation script for the Streamlit app.
Checks that all domains are properly configured and can be imported.
"""
import sys
import os


def validate_imports():
    """Validate that all domain modules can be imported."""
    print("=" * 60)
    print("VALIDATING DOMAIN IMPORTS")
    print("=" * 60)

    domains = [
        ("trees", "trees_app", "render_trees_app"),
        ("exercise", "exercise_app", "render_exercise_app"),
        ("finance", "finance_app", "render_finance_app"),
        ("task_management", "task_management_app", "render_task_management_app"),
        ("travel", "travel_app", "render_travel_app"),
    ]

    all_passed = True

    for domain_name, module_name, function_name in domains:
        module_path = f"domains.{domain_name}.{module_name}"
        try:
            module = __import__(module_path, fromlist=[function_name])
            func = getattr(module, function_name)
            print(f"✓ {domain_name:20s} - {function_name} imported successfully")
        except Exception as e:
            print(f"✗ {domain_name:20s} - FAILED: {e}")
            all_passed = False

    return all_passed


def validate_structure():
    """Validate that domain folder structure exists."""
    print("\n" + "=" * 60)
    print("VALIDATING DOMAIN STRUCTURE")
    print("=" * 60)

    domains = ["trees", "exercise", "finance", "task_management", "travel"]
    all_passed = True

    for domain in domains:
        domain_path = f"domains/{domain}"
        data_path = f"domains/{domain}/{domain}_data"
        app_file = f"domains/{domain}/{domain}_app.py"

        if not os.path.exists(domain_path):
            print(f"✗ {domain:20s} - domain folder missing")
            all_passed = False
            continue

        if not os.path.exists(data_path):
            print(f"⚠ {domain:20s} - data folder missing (creating...)")
            os.makedirs(data_path, exist_ok=True)

        if not os.path.exists(app_file):
            print(f"✗ {domain:20s} - app.py file missing")
            all_passed = False
        else:
            print(f"✓ {domain:20s} - structure valid")

    return all_passed


def validate_main_files():
    """Validate that main application files exist."""
    print("\n" + "=" * 60)
    print("VALIDATING MAIN APPLICATION FILES")
    print("=" * 60)

    files = [
        ("app.py", "Main application file"),
        ("app_cfg.py", "Configuration file"),
        ("requirements.txt", "Dependencies file"),
    ]

    all_passed = True

    for filename, description in files:
        if os.path.exists(filename):
            print(f"✓ {filename:20s} - {description}")
        else:
            print(f"✗ {filename:20s} - MISSING: {description}")
            all_passed = False

    return all_passed


def main():
    """Run all validation checks."""
    print("\n" + "=" * 60)
    print("STREAMLIT APP VALIDATION")
    print("=" * 60 + "\n")

    # Change to the script directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    results = []

    # Run validation checks
    results.append(("Main Files", validate_main_files()))
    results.append(("Domain Structure", validate_structure()))
    results.append(("Domain Imports", validate_imports()))

    # Summary
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)

    all_passed = all(passed for _, passed in results)

    for check_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{check_name:20s} - {status}")

    print("=" * 60)

    if all_passed:
        print("\n✓ ALL CHECKS PASSED!")
        print("\nYou can now run the app with:")
        print("  streamlit run app.py")
        return 0
    else:
        print("\n✗ SOME CHECKS FAILED")
        print("\nPlease fix the issues above before running the app.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
