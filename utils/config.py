'''
    This code creates, reads, and updates a config.json file in the same directory as the executable or sbript.
    The config file is used to store the folder path for the receipts.
    
    Seongjun Yoo
'''

import re
import sys
import json
from pathlib import Path

# Path building
def get_config_path() -> Path:
    if getattr(sys, "frozen", False):
        base = Path(sys.executable).parent
    else:
        base = Path(__file__).parent
    return base / "config.json"

# Check if config file exist, if not create one
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

# Create folders for each card number and a "others" folder in the destination directory
def create_folders(config: dict):
    parent_directory = Path(config["dest"])
    for card in config.get("cards"):
        if card:
            Path(parent_directory / card).mkdir(parents=True, exist_ok=True)
    
    Path(parent_directory / "others").mkdir(parents=True, exist_ok=True)

def create_store_folders(config: dict):
    parent_directory = Path(config["dest"])

    for card in config.get("cards"):
        if card:
            Path(parent_directory / card / "unknown_store").mkdir(parents=True, exist_ok=True)
            
            for store in config.get("stores"):
                if store:
                    Path(parent_directory / card / store).mkdir(parents=True, exist_ok=True)
        
    
    for store in config.get("stores"):
        Path(parent_directory / "others" / store).mkdir(parents=True, exist_ok=True)



def setup_wizard(config: dict) -> dict:
    print("=" * 50)
    print("  Receipt Auto-Renamer - First Time Setup")
    print("=" * 50)
    print()
    print("Source Folder")
    print(r"  Example: C:\Users\Example\Receipts")
    print()
    print("Destination Folder")
    print(r"  Example: C:\Users\Exmaple\Done")
    while True:
        source = input("  Source path: ").strip().strip('"')
        dest = input ("  Destination path: ").strip().strip('"')
        if (source and Path(source).exists()) and (dest and Path(dest).exists()):
            config["source"] = source
            config["dest"] = dest
            break
        elif source:
            print(f"  Folder not found: {source}. Please check and try again.")
        else:
            print("  Folder path cannot be empty.")
    

    print()
    print("Frequent Card Numbers (Optional, this will create folders for each card number + others folder)")
    print("  Enter the last 4 digits of your cards, separated by commas.")
    print("  Example: 1234,5678,9012")
    cardNumbers = input("  Cards (Press Enter to skip): ").strip()

    print()
    print("Subfolder naming: (Mendatory, if not entered, every files will be inside a single folder. This will create folders named after store to separate receipts by store)")
    print("  Enter the store names, separated by commas.\n Example: Walmart, Sobeys, ... ")
    storeNames = input(" Store names (Press Enter to skip): ").strip()
    
    config["cards"] = [c.strip() for c in cardNumbers.split(",")]
    config["stores"] = [s.strip() for s in storeNames.split(",")]
    
    print()
    save_config(config)
    create_folders(config)
    create_store_folders(config)
    return config
