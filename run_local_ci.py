#!/usr/bin/env python3
"""Run GitHub Actions CI jobs locally for faster development iteration."""
import subprocess
import sys
import os
from pathlib import Path

def run_command(name, command, description):
    """Run a command and display result."""
    print(f"\n{'='*60}")
    print(f"Running: {name}")
    print(f"Description: {description}")
    print(f"{'='*60}\n")

    result = subprocess.run(command, shell=True)

    if result.returncode == 0:
        print(f"\n[SUCCESS] {name} passed!")
        return True
    else:
        print(f"\n[FAILED] {name} failed with exit code {result.returncode}")
        return False

def run_syntax_check():
    """Run Python syntax check locally."""
    return run_command(
        "Python Syntax Check",
        "python .github/scripts/syntax_check.py",
        "Validate Python syntax for all files"
    )

def run_lint_check():
    """Run linting check locally."""
    return run_command(
        "Code Linting",
        "pyflakes main.py core/*.py core/ui/*.py",
        "Check code quality with pyflakes"
    )

def run_import_check():
    """Run import validation locally."""
    return run_command(
        "Import Validation",
        "python -c \"import main, core.overlay, core.input_mon, core.settings_manager, core.configuration, core.gui, core.ui.components, core.logging_config\"",
        "Test all module imports"
    )

def run_type_check():
    """Run type validation locally."""
    return run_command(
        "Type Validation",
        "python .github/scripts/type_check.py",
        "Validate type hints in all files"
    )

def run_config_validation():
    """Run configuration validation locally."""
    return run_command(
        "Configuration Validation",
        "python .github/scripts/config_validation.py",
        "Validate configuration schema and operations"
    )

def run_build_test():
    """Run build test locally."""
    return run_command(
        "Windows Build Test",
        "python build.py",
        "Test PyInstaller build process"
    )

def run_all_checks():
    """Run all CI checks sequentially."""
    checks = [
        ("Syntax Check", run_syntax_check),
        ("Linting Check", run_lint_check),
        ("Import Check", run_import_check),
        ("Type Check", run_type_check),
        ("Config Check", run_config_validation),
        ("Build Test", run_build_test),
    ]

    results = {}
    for name, check_func in checks:
        results[name] = check_func()

    # Print summary
    print(f"\n{'='*60}")
    print("LOCAL CI SUMMARY")
    print(f"{'='*60}\n")

    all_passed = True
    for name, passed in results.items():
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} {name}")
        if not passed:
            all_passed = False

    print(f"\n{'='*60}")
    if all_passed:
        print("ALL CHECKS PASSED!")
    else:
        print("SOME CHECKS FAILED!")
    print(f"{'='*60}\n")

    return 0 if all_passed else 1

def main():
    """Main entry point."""
    print("Local GitHub Actions CI Runner")
    print("="*60)
    print("\nThis script runs all CI checks locally for faster development.")
    print("\nUsage:")
    print("  python run_local_ci.py              # Run all checks")
    print("  python run_local_ci.py --syntax    # Run only syntax check")
    print("  python run_local_ci.py --lint      # Run only linting")
    print("  python run_local_ci.py --import    # Run only import check")
    print("  python run_local_ci.py --type      # Run only type check")
    print("  python run_local_ci.py --config    # Run only config check")
    print("  python run_local_ci.py --build     # Run only build test")
    print("\n" + "="*60 + "\n")

    # Parse arguments
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()

        if arg == '--syntax':
            sys.exit(0 if run_syntax_check() else 1)
        elif arg == '--lint':
            sys.exit(0 if run_lint_check() else 1)
        elif arg == '--import':
            sys.exit(0 if run_import_check() else 1)
        elif arg == '--type':
            sys.exit(0 if run_type_check() else 1)
        elif arg == '--config':
            sys.exit(0 if run_config_validation() else 1)
        elif arg == '--build':
            sys.exit(0 if run_build_test() else 1)
        else:
            print(f"Unknown argument: {arg}")
            print("\nRun 'python run_local_ci.py' for usage.")
            sys.exit(1)
    else:
        # Run all checks
        sys.exit(run_all_checks())

if __name__ == "__main__":
    main()
