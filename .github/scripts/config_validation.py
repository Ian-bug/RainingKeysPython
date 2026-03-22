#!/usr/bin/env python3
"""Configuration validation script for GitHub Actions CI."""
import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Suppress Qt warnings for CI
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

def validate_config():
    """Validate configuration schema and operations."""
    try:
        from core.settings_manager import SettingsManager
        from core.configuration import AppConfig

        print("Testing configuration validation...")

        # Test default config
        config = AppConfig()
        print("[OK] Default configuration created successfully")

        # Test schema validation
        settings = SettingsManager()
        print("[OK] Schema validation passed")

        # Test config save
        import tempfile
        temp_config = tempfile.mktemp(suffix='.ini')
        try:
            settings.filename = temp_config
            settings.save()
            print("[OK] Config save works correctly")
        finally:
            if os.path.exists(temp_config):
                os.remove(temp_config)

        print("\nAll configuration validation checks passed!")
        return True

    except Exception as e:
        print(f"[ERROR] Configuration validation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if not validate_config():
        sys.exit(1)
