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
    print(r"  Example: C:\Users\jjunn\OneDrive\Receipts")
    print()
    while True:
        folder = input("  Folder path: ").strip().strip('"')
        if folder and Path(folder).exists():
            config["folder"] = folder
            break
        elif folder:
            print(f"  Folder not found: {folder}. Please check and try again.")
        else:
            print("  Folder path cannot be empty.")
    print()
    save_config(config)
    return config