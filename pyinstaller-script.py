#!/usr/bin/env python3
"""
PyInstaller setup for Directory Tree Creator

This script will create a standalone executable for the Directory Tree Creator application.
It automatically finds and uses any icon in the 'icons' folder.
"""

import PyInstaller.__main__
import os
import sys
import glob
import subprocess
import shutil


def check_dependencies():
    """Check if required dependencies are installed and install them if needed."""
    try:
        import PyInstaller
    except ImportError:
        print("PyInstaller not found. Installing...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "PyInstaller"])
        except subprocess.CalledProcessError:
            print("Failed to install PyInstaller. Please install it manually with:")
            print("pip install pyinstaller")
            sys.exit(1)
    
    try:
        from PIL import Image
    except ImportError:
        print("Pillow not found. Installing...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
        except subprocess.CalledProcessError:
            print("Failed to install Pillow. Please install it manually with:")
            print("pip install Pillow")
            sys.exit(1)


def find_icon():
    """Find the first valid icon in the icons folder."""
    # Create icons directory if it doesn't exist
    if not os.path.exists('icons'):
        os.makedirs('icons')
        print("Created 'icons' folder. Please add your icon file to this folder.")
        return None
    
    # Look for icon files in order of preference
    for ext in ['.ico', '.png', '.jpg', '.jpeg']:
        icons = glob.glob(f'icons/*{ext}')
        if icons:
            # Return the first icon found
            return os.path.abspath(icons[0])
    
    print("No icon files found in the 'icons' folder.")
    print("Looking for icons in the current directory...")
    
    # Fall back to current directory
    for ext in ['.ico', '.png', '.jpg', '.jpeg']:
        icons = glob.glob(f'*{ext}')
        if icons:
            # Return the first icon found
            return os.path.abspath(icons[0])
    
    return None


def open_output_folder():
    """Open the dist folder in file explorer."""
    dist_path = os.path.abspath('dist')
    
    if os.path.exists(dist_path):
        # Platform-specific commands to open folder
        if sys.platform == 'win32':
            os.startfile(dist_path)
        elif sys.platform == 'darwin':  # macOS
            subprocess.call(['open', dist_path])
        else:  # Linux
            subprocess.call(['xdg-open', dist_path])


def build_executable():
    """Build the executable with PyInstaller."""
    # Check for dependencies first
    check_dependencies()
    
    # Define script name
    script_name = 'directory_tree_creator_gui.py'
    output_name = 'DirectoryTreeCreator'
    
    # Check if the script exists
    if not os.path.exists(script_name):
        script_files = glob.glob('*.py')
        if not script_files:
            print(f"Error: Could not find {script_name} or any Python files.")
            sys.exit(1)
        script_name = script_files[0]
        print(f"Using {script_name} as the main script file.")
    
    # Find icon
    icon_path = find_icon()
    
    # Define PyInstaller arguments
    pyinstaller_args = [
        script_name,                  # Your script name
        '--onefile',                  # Create a single executable
        '--windowed',                 # Don't show console window
        f'--name={output_name}',      # Name of the output executable
        '--clean',                    # Clean PyInstaller cache
        '--noupx',                    # Don't use UPX (more compatible)
    ]
    
    # Add icon if found
    if icon_path:
        print(f"Using icon: {icon_path}")
        pyinstaller_args.append(f'--icon={icon_path}')
    else:
        print("No icon found. Building without custom icon.")
    
    # Clean old build files if they exist
    for folder in ['build', 'dist']:
        if os.path.exists(folder):
            try:
                shutil.rmtree(folder)
                print(f"Removed old {folder} folder")
            except Exception as e:
                print(f"Warning: Could not remove old {folder} folder: {e}")
    
    if os.path.exists(f"{output_name}.spec"):
        try:
            os.remove(f"{output_name}.spec")
            print("Removed old .spec file")
        except Exception as e:
            print(f"Warning: Could not remove old .spec file: {e}")
    
    # Run PyInstaller
    print("\nBuilding executable with PyInstaller...")
    try:
        PyInstaller.__main__.run(pyinstaller_args)
        print("\nBuild completed successfully!")
        print(f"Executable created: dist/{output_name}.exe")
        
        # Open the output folder
        open_output_folder()
        
    except Exception as e:
        print(f"\nError building executable: {e}")
        
        if icon_path and '--icon' in str(e):
            print("\nThere might be an issue with the icon file.")
            print("Trying to build without the icon...")
            
            # Remove icon argument and try again
            if f'--icon={icon_path}' in pyinstaller_args:
                pyinstaller_args.remove(f'--icon={icon_path}')
            
            try:
                PyInstaller.__main__.run(pyinstaller_args)
                print("\nBuild completed successfully without custom icon!")
                print(f"Executable created: dist/{output_name}.exe")
                
                # Open the output folder
                open_output_folder()
            except Exception as e2:
                print(f"\nError building executable without icon: {e2}")
                sys.exit(1)


if __name__ == "__main__":
    print("=" * 60)
    print("Directory Tree Creator - Executable Builder")
    print("=" * 60)
    
    build_executable()
    
    print("\nPress Enter to exit...")
    input()