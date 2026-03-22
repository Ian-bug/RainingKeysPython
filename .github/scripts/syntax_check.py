#!/usr/bin/env python3
"""Python syntax check script for GitHub Actions CI."""
import os
import py_compile
import sys

def check_directory(directory):
    """Check all Python files in a directory."""
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                try:
                    py_compile.compile(filepath, doraise=True)
                    print(f"[OK] {filepath}")
                except py_compile.PyCompileError as e:
                    print(f"[FAILED] {filepath}: {e}")
                    return False
    return True

# Check main.py
try:
    py_compile.compile('main.py', doraise=True)
    print("[OK] main.py")
except py_compile.PyCompileError as e:
    print(f"[FAILED] main.py: {e}")
    sys.exit(1)

# Check core/ directory
if not check_directory('core'):
    sys.exit(1)

# Check core/ui/ directory
if not check_directory('core/ui'):
    sys.exit(1)

print("\nAll files compiled successfully!")
