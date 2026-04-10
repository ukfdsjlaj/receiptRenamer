"""
    Receipt Auto-Renamer
    --------------------------------------
    Renames scanned receipt file to: 1234 2024-03-23 StoreName.fileExtension
    and moves them to a destination folder.

    - Automatically installs Ollama if not found
    - Automatically starts Ollama if not running
    - Automatically pulls llama3.2-vision if not downloaded
    - No API key needed — runs fully on PC using Ondevice AI (Ollama)

    Seongjun Yoo
"""

import sys
from pathlib import Path

# Custom modules
from utils import config, ollamaSetup, pdfProcessing

def main():
    print("Receipt Auto-Renamer")
    print("=" * 50)
    print()

    # Ensure Ollama is installed and fully funcitoning
    ollamaSetup.ensure_ollama_ready()

    # Load or create config
    cfg = config.load_config()
    if not cfg.get("folder") or not cfg.get("dest"):
        cfg = config.setup_wizard(cfg)
    else:
        print(f"Source      : {cfg['folder']}")
        print(f"Destination : {cfg['dest']}")
        print("(Delete config.json to change folders)\n")

    folder = Path(cfg["folder"])
    dest   = Path(cfg["dest"])

    if not folder.exists():
        print(f"Source folder not found: {folder}")
        print("Delete config.json and run again.")
        input("\nPress Enter to exit...")
        return

    if not dest.exists():
        print(f"Destination folder not found: {dest}")
        print("Delete config.json and run again.")
        input("\nPress Enter to exit...")
        return

    valid_extensions = [".pdf", ".jpg", ".jpeg", ".png"]
    files_to_process = [p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in valid_extensions]
    
    # Sort them alphabetically
    files_to_process.sort()

    if not files_to_process:
        print(f"No receipts (PDF/JPG/PNG) found in: {folder}")
        input("\nPress Enter to exit...")
        return

    print(f"Found {len(files_to_process)} file(s)")
    print("Note: First receipt may be slow while model loads into memory.\n")

    existing_names = {p.name.lower() for p in dest.iterdir()}
    moved   = 0
    skipped = 0

    for file_path in files_to_process:
        known_cards = cfg.get("cards", [])
        info = pdfProcessing.extract_receipt_info(file_path, known_cards) # Pass the file to AI
        
        card  = info.get("card")
        date  = info.get("date")
        store = info.get("store")

        # Skip if any of one info is missing
        missing = [f for f, v in [("card", card), ("date", date), ("store", store)] if not v]
        if missing:
            print(f"  SKIP {file_path.name} - could not read: {', '.join(missing)}")
            skipped += 1
            continue

        # Rename but keep the original extension
        ext = file_path.suffix.lower()
        new_name = pdfProcessing.build_new_filename(card, date, store, existing_names, ext)
        existing_names.add(new_name.lower())

        try:
            file_path.rename(dest / new_name)
            print(f"  {file_path.name} -> {new_name}")
            moved += 1
        except Exception as e:
            print(f"  Failed to move {file_path.name}: {e}")
            skipped += 1

    print()
    print(f"Done. {moved} file(s) renamed and moved, {skipped} skipped.")
    input("\nPress Enter to exit...")

# RUNNNNNNN
if __name__ == "__main__":
    main()