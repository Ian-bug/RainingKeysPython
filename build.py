import configparser
import os
import shutil
import subprocess
import sys

CONFIG_FILES = ['config.ini', 'config.cfg']
OUTPUT_DIR = 'dist'
BUILD_DIR = 'build'
EXECUTABLE_NAME = 'RainingKeysPython'
MAIN_SCRIPT = 'main.py'

def read_config():
    """
    Reads debug_mode from config.ini or config.cfg.
    Returns boolean: True (Debug), False (Release).
    Defaults to False if not specified.
    """
    config = configparser.ConfigParser()
    
    # Try to read config files
    found_files = config.read(CONFIG_FILES)
    if not found_files:
        print(f"Warning: No config file found ({'/'.join(CONFIG_FILES)}). Defaulting to Release mode.")
        return False

    # Check for debug_mode in [General] section (or others if widely used)
    # We prioritize [General] > [Debug] > global search if needed, but [General] is standard.
    if config.has_section('General'):
        if config.has_option('General', 'debug_mode'):
            return config.getboolean('General', 'debug_mode')
            
    # Fallback: check if it's in a [Debug] section
    if config.has_section('Debug'):
        if config.has_option('Debug', 'debug_mode'):
            return config.getboolean('Debug', 'debug_mode')

    print("Info: 'debug_mode' not found in config. Defaulting to Release mode.")
    return False

def clean_directories():
    """Removes build and dist directories."""
    dirs_to_clean = [OUTPUT_DIR, BUILD_DIR]
    for d in dirs_to_clean:
        if os.path.exists(d):
            print(f"Cleaning {d}...")
            shutil.rmtree(d)

def build(debug_mode):
    """Invokes PyInstaller to build the executable."""
    print(f"Building {EXECUTABLE_NAME} (Debug Mode: {debug_mode})...")
    
    cmd = [
        'pyinstaller',
        '--onedir',
        '--clean',
        '--name', EXECUTABLE_NAME,
        MAIN_SCRIPT
    ]

    if not debug_mode:
        cmd.extend(['--noconsole', '--windowed'])
    # Else: keep console (default behavior for pyinstaller without --noconsole)

    # Note: We don't explicitly add --add-data here because we copy config manually after build.
    # If hidden imports are needed (e.g. pynput, PySide6), PyInstaller usually finds them.
    # If issues arise, we can add --hidden-import.
    
    # Run PyInstaller
    subprocess.check_call(cmd)

def copy_config_to_dist():
    """Copies the existing config file to the dist directory."""
    target_dir = os.path.join(OUTPUT_DIR, EXECUTABLE_NAME)
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    copied = False
    for cfg in CONFIG_FILES:
        if os.path.exists(cfg):
            input_config = cfg
            shutil.copy2(input_config, target_dir)
            print(f"Copied {input_config} to {target_dir}")
            copied = True
            break
    
    if not copied:
        print("Warning: No config file found to copy.")

def create_zip(debug_mode):
    """Packages the dist folder into a zip file."""
    source_dir = os.path.join(OUTPUT_DIR, EXECUTABLE_NAME)
    
    zip_name = EXECUTABLE_NAME
    if debug_mode:
        zip_name += "-debug"
    
    # shutil.make_archive expects the base_name without extension
    # It creates base_name.zip
    
    print(f"\nPackaging into {zip_name}.zip...")
    
    # format='zip': create a zip file
    # root_dir=OUTPUT_DIR: the root directory to archive
    # base_dir=EXECUTABLE_NAME: the directory inside root_dir to start archiving from
    # This prevents the zip from containing 'dist/...' structure, but rather just the executable folder
    
    # We want the zip to contain the top-level folder 'RainingKeysPython'
    # So we archive 'dist' but only the 'RainingKeysPython' subdirectory
    
    shutil.make_archive(zip_name, 'zip', root_dir=OUTPUT_DIR, base_dir=EXECUTABLE_NAME)
    print(f"Zip created: {zip_name}.zip")

def main():
    # 1. Clean previous builds
    clean_directories()

    # 2. Determine mode
    debug_mode = read_config()

    # 3. Build
    try:
        build(debug_mode)
    except subprocess.CalledProcessError as e:
        print(f"Error during build: {e}")
        sys.exit(1)
    except FileNotFoundError:
         print("Error: 'pyinstaller' not found. Please install it via 'pip install pyinstaller'.")
         sys.exit(1)

    # 4. Copy config
    copy_config_to_dist()

    # 5. Zip
    create_zip(debug_mode)

    print("\nBuild and packaging complete!")
    print(f"Output folder: {os.path.join(OUTPUT_DIR, EXECUTABLE_NAME)}")
    print(f"Zip file: {EXECUTABLE_NAME + ('-debug' if debug_mode else '')}.zip")

if __name__ == "__main__":
    main()
