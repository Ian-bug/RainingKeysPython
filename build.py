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
        '--noconfirm',
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

def update_config_debug_mode(debug_mode):
    """Updates config.ini to match the current build mode."""
    # We read the config to preserve other settings, but force debug_mode
    config = configparser.ConfigParser()
    config.read(CONFIG_FILES)
    
    # Ensure sections exist
    if not config.has_section('General'):
        if config.has_section('Debug'):
            # Legacy support if user uses [Debug]
            config.set('Debug', 'debug_mode', str(debug_mode))
        else:
            config.add_section('General')
            config.set('General', 'debug_mode', str(debug_mode))
    else:
         config.set('General', 'debug_mode', str(debug_mode))
    
    # Write back
    # We pick the first available config file to write to, usually config.ini
    target_cfg = CONFIG_FILES[0]
    with open(target_cfg, 'w') as f:
        config.write(f)

def run_build_cycle(debug_mode):
    print(f"\n>>> Starting {'DEBUG' if debug_mode else 'RELEASE'} Build Cycle <<<")
    
    # Update config file so the built executable reads the correct mode at runtime
    # AND so that the copy_config_to_dist puts the correct config in the dist folder
    update_config_debug_mode(debug_mode)
    
    # Build
    try:
        build(debug_mode)
    except subprocess.CalledProcessError as e:
        print(f"Error during build: {e}")
        sys.exit(1)
        
    # Copy Config
    copy_config_to_dist()
    
    # Zip
    create_zip(debug_mode)

def main():
    # 1. Clean previous builds once at the start
    clean_directories()

    # 2. Check dependencies
    try:
        subprocess.call(['pyinstaller', '--version'], stdout=subprocess.DEVNULL)
    except FileNotFoundError:
         print("Error: 'pyinstaller' not found. Please install it via 'pip install pyinstaller'.")
         sys.exit(1)

    # 3. Release Build (Normal)
    run_build_cycle(debug_mode=False)
    
    # 4. Debug Build
    # We clean build/ between runs to ensure clean state, but NOT dist/ (so we keep the zips)
    if os.path.exists(BUILD_DIR):
        shutil.rmtree(BUILD_DIR)
        
    run_build_cycle(debug_mode=True)

    print("\nAll builds complete!")
    print(f"Artifacts located in project root:")
    print(f" - {EXECUTABLE_NAME}.zip")
    print(f" - {EXECUTABLE_NAME}-debug.zip")

if __name__ == "__main__":
    main()
