import subprocess
import time
import sys
import os

# Folder where your scripts live
SCRIPT_DIR = os.path.join(os.path.dirname(__file__), "scripts")

# List of scripts to run (in order)
scripts = [
    "normalize_properties.py",
    "transactions.py",
    "properties.py"
]

for script in scripts:
    script_path = os.path.join(SCRIPT_DIR, script)
    print(f"\n▶️ Running {script}...")
    try:
        subprocess.run([sys.executable, script_path], check=True)
        print(f"✅ {script} completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"❌ {script} failed with error code {e.returncode}.")
        break

    # Delay between scripts
    time.sleep(5)

print("\n🎯 All scripts completed.")
