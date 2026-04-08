'''
    This code creates, reads, and updates a config.json file in the same directory as the executable or sbript.
    The config file is used to store the folder path for the receipts.
    
    Seongjun Yoo
'''

import sys
import json
from pathlib import Path

def get_config_path() -> Path:
    if getattr(sys, "frozen", False):
        base = Path(sys.executable).parent
    else:
        base = Path(__file__).parent
    return base / "config.json"

def load_config() -> dict:
    path = get_config_path()
    if path.exists():
        try:
            with open(path) as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_config(config: dict):
    with open(get_config_path(), "w") as f:
        json.dump(config, f, indent=2)
    print(f"  Settings saved to: {get_config_path()}\n")

def setup_wizard(config: dict) -> dict:
    print("=" * 50)
    print("  Receipt Auto-Renamer - First Time Setup")
    print("=" * 50)
    print()
    print("Receipts Folder")
    print(r"  Example: C:\Users\Example\Receipts")
    print()
    print("Destination Folder")
    print(r"  Example: C:\Users\Exmaple\Done")
    while True:
        folder = input("  Folder path: ").strip().strip('"')
        dest = input ("  Folder path: ").strip().strip('"')
        if (folder and Path(folder).exists()) and (dest and Path(dest).exists()):
            config["folder"] = folder
            config["dest"] = dest
            break
        elif folder:
            print(f"  Folder not found: {folder}. Please check and try again.")
        else:
            print("  Folder path cannot be empty.")
    print()
    save_config(config)
    return config