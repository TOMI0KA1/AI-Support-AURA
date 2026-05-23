import subprocess
import sys
import os
import shutil

def build_exe():
    print("🚀 Starting Aura build process...")

    # Define paths
    main_script = "aura_optimized_launcher.py"
    app_name = "AuraAssistant"

    # Build command
    cmd = [
        "pyinstaller",
        "--noconfirm",
        "--onefile",
        "--windowed",
        f"--name={app_name}",
        "--add-data=src;src",
        "--add-data=assets;assets",
        # "--icon=assets/icon.ico", # Uncomment if you have an icon
        main_script
    ]

    print(f"Running command: {' '.join(cmd)}")

    try:
        subprocess.check_call(cmd)
        print(f"✅ Build successful! You can find the executable in the 'dist' folder.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    build_exe()
