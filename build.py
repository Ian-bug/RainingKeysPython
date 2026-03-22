import configparser
import os
import shutil
import subprocess
import sys
import logging

# Setup basic logging for build script
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

from core.settings_manager import SettingsManager

CONFIG_FILES = ['config.ini', 'config.cfg']
OUTPUT_DIR = 'dist'
BUILD_DIR = 'build'
EXECUTABLE_NAME = 'RainingKeysPython'
MAIN_SCRIPT = 'main.py'



def clean_directories() -> bool:
    """Removes build and dist directories.

    Returns:
        True if cleanup succeeded, False if errors occurred.
    """
    dirs_to_clean = [OUTPUT_DIR, BUILD_DIR]
    success = True
    for d in dirs_to_clean:
        if os.path.exists(d):
            logger.info(f"Cleaning {d}...")
            try:
                shutil.rmtree(d)
            except (IOError, OSError, PermissionError) as e:
                logger.error(f"Failed to clean {d}: {e}")
                success = False
    return success

def build(debug_mode):
    """Invokes PyInstaller to build the executable."""
    logger.info(f"Building {EXECUTABLE_NAME} (Debug Mode: {debug_mode})...")

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
            logger.info(f"Copied {input_config} to {target_dir}")
            copied = True
            break

    if not copied:
        logger.warning("No config file found to copy.")

def create_zip(debug_mode):
    """Packages the dist folder into a zip file."""
    source_dir = os.path.join(OUTPUT_DIR, EXECUTABLE_NAME)

    zip_name = EXECUTABLE_NAME
    if debug_mode:
        zip_name += "-debug"

    # shutil.make_archive expects the base_name without extension
    # It creates base_name.zip

    logger.info(f"Packaging into {zip_name}.zip...")

    # format='zip': create a zip file
    # root_dir=OUTPUT_DIR: the root directory to archive
    # base_dir=EXECUTABLE_NAME: the directory inside root_dir to start archiving from
    # This prevents the zip from containing 'dist/...' structure, but rather just the executable folder

    # We want the zip to contain the top-level folder 'RainingKeysPython'
    # So we archive 'dist' but only the 'RainingKeysPython' subdirectory

    shutil.make_archive(zip_name, 'zip', root_dir=OUTPUT_DIR, base_dir=EXECUTABLE_NAME)
    logger.info(f"Zip created: {zip_name}.zip")

def update_config_debug_mode(debug_mode: bool) -> bool:
    """Updates config.ini to match the current build mode.

    Handles multiple encodings gracefully and provides detailed error messages.

    Args:
        debug_mode: Whether to enable debug mode in config.

    Returns:
        True if config update succeeded, False otherwise.
    """
    # We read the config to preserve other settings, but force debug_mode
    config = configparser.ConfigParser()

    # Try multiple encodings for reading
    encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
    read_success = False

    for cfg in CONFIG_FILES:
        if os.path.exists(cfg):
            for encoding in encodings:
                try:
                    with open(cfg, 'r', encoding=encoding) as f:
                        config.read_file(f)
                    logger.info(f"Successfully read {cfg} with encoding {encoding}")
                    read_success = True
                    break
                except (UnicodeDecodeError, UnicodeError):
                    continue
                except Exception as e:
                    logger.warning(f"Failed to read {cfg} with encoding {encoding}: {e}")
            if read_success:
                break

    if not read_success:
        logger.warning("Could not read existing config, starting fresh")

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

    # Write back with UTF-8
    try:
        target_cfg = CONFIG_FILES[0]
        with open(target_cfg, 'w', encoding='utf-8') as f:
            config.write(f)
        logger.debug(f"Updated debug_mode to {debug_mode} in {target_cfg}")
        return True
    except (IOError, OSError, PermissionError) as e:
        logger.error(f"Failed to write config file {target_cfg}: {e}")
        return False

def run_build_cycle(debug_mode: bool) -> None:
    """Execute a single build cycle (clean, config, build, copy, zip).

    Args:
        debug_mode: Whether this is a debug build.
    """
    logger.info(f"\n>>> Starting {'DEBUG' if debug_mode else 'RELEASE'} Build Cycle <<<")

    # Reset config to defaults if building for Release
    if not debug_mode:
        logger.info("Resetting configuration to defaults for Release build...")
        try:
            settings = SettingsManager()
            settings.reset_to_defaults()
            logger.info("Configuration reset successful.")
        except Exception as e:
            logger.warning(f"Failed to reset configuration: {e}")

    # Update config file so the built executable reads the correct mode at runtime
    # AND so that the copy_config_to_dist puts the correct config in the dist folder
    if not update_config_debug_mode(debug_mode):
        logger.error("Failed to update config debug mode, continuing anyway...")

    # Build
    try:
        build(debug_mode)
    except subprocess.CalledProcessError as e:
        logger.error(f"Error during build: {e}")
        sys.exit(1)

    # Copy Config
    copy_config_to_dist()

    # Zip
    create_zip(debug_mode)

def main() -> None:
    """Main build entry point.

    Executes both release and debug builds.
    """
    # 1. Clean previous builds once at the start
    clean_directories()

    # 2. Check dependencies
    try:
        subprocess.call(['pyinstaller', '--version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        logger.error("'pyinstaller' not found. Please install it via 'pip install pyinstaller'.")
        sys.exit(1)

    # 3. Release Build (Normal)
    run_build_cycle(debug_mode=False)

    # 4. Debug Build
    # We clean build/ between runs to ensure clean state, but NOT dist/ (so we keep the zips)
    if os.path.exists(BUILD_DIR):
        try:
            shutil.rmtree(BUILD_DIR)
        except Exception as e:
            logger.warning(f"Failed to clean build directory: {e}")

    run_build_cycle(debug_mode=True)

    logger.info("\nAll builds complete!")
    logger.info(f"Artifacts located in project root:")
    logger.info(f" - {EXECUTABLE_NAME}.zip")
    logger.info(f" - {EXECUTABLE_NAME}-debug.zip")

if __name__ == "__main__":
    main()
