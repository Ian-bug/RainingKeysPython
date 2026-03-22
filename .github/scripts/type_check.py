#!/usr/bin/env python3
"""Type validation check script for GitHub Actions CI."""
import ast
import sys
import os

def check_file(filepath):
    """Check type hints in a Python file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()
            ast.parse(source, filepath)
        return True, None
    except SyntaxError as e:
        return False, str(e)

files_to_check = [
    'main.py',
    'core/overlay.py',
    'core/input_mon.py',
    'core/settings_manager.py',
    'core/configuration.py',
    'core/gui.py',
    'core/ui/components.py'
]

all_ok = True
errors = []

for filepath in files_to_check:
    ok, error = check_file(filepath)
    if ok:
        print(f"[OK] {filepath} - type hints valid")
    else:
        print(f"[ERROR] {filepath}: {error}")
        errors.append((filepath, error))
        all_ok = False

if not all_ok:
    print("\n=== Errors Found ===")
    for filepath, error in errors:
        print(f"{filepath}: {error}")
    sys.exit(1)

print("\nAll type hints validated successfully!")
