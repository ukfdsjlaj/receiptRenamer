"""
    Receipt Auto-Renamer
    --------------------------------------
    Renames scanned receipt PDFs to: 1234 2024-03-23 StoreName.pdf
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

    # Ensure Ollama is installed, running, and model is ready
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

    pdfs = sorted(folder.glob("*.pdf"))
    if not pdfs:
        print(f"No PDF files found in: {folder}")
        input("\nPress Enter to exit...")
        return

    print(f"Found {len(pdfs)} PDF(s)")
    print("Note: First receipt may be slow while model loads into memory.\n")

    existing_names = {p.name.lower() for p in dest.iterdir()}
    moved   = 0
    skipped = 0

    for pdf in pdfs:
        known_cards = cfg.get("cards", [])
        
        info = pdfProcessing.extract_receipt_info(pdf, known_cards)
        card  = info.get("card")
        date  = info.get("date")
        store = info.get("store")

        missing = [f for f, v in [("card", card), ("date", date), ("store", store)] if not v]
        if missing:
            print(f"  SKIP {pdf.name} - could not read: {', '.join(missing)}")
            skipped += 1
            continue

        new_name = pdfProcessing.build_new_filename(card, date, store, existing_names)
        existing_names.add(new_name.lower())

        try:
            pdf.rename(dest / new_name)
            print(f"  {pdf.name} -> {new_name}")
            moved += 1
        except Exception as e:
            print(f"  Failed to move {pdf.name}: {e}")
            skipped += 1

    print()
    print(f"Done. {moved} file(s) renamed and moved, {skipped} skipped.")
    input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()