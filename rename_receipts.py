"""
Receipt Auto-Renamer (Ollama Edition)
--------------------------------------
Renames scanned receipt PDFs to: 1234 2024-03-23 StoreName.pdf

- Automatically installs Ollama if not found
- Automatically starts Ollama if not running
- Automatically pulls llama3.2-vision if not downloaded
- No API key needed — runs fully on your PC
"""

import sys
from pathlib import Path

# Custom modules
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
    if not cfg.get("folder"):
        cfg = config.setup_wizard(cfg)
    else:
        print(f"Folder : {cfg['folder']}")
        print("(Delete config.json to change folder)\n")

    folder = Path(cfg["folder"])
    if not folder.exists():
        print(f"Receipts folder not found: {folder}")
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

    # Preview
    print("Preview (no files renamed yet):")
    print("-" * 40)

    existing_names = {p.name.lower() for p in folder.iterdir()}
    planned = []

    for pdf in pdfs:
        info = pdfProcessing.extract_receipt_info(pdf)
        card  = info.get("card")
        date  = info.get("date")
        store = info.get("store")

        missing = [f for f, v in [("card", card), ("date", date), ("store", store)] if not v]
        if missing:
            print(f"  SKIP {pdf.name} - could not read: {', '.join(missing)}")
            planned.append((pdf, None))
            continue

        new_name = pdfProcessing.build_new_filename(card, date, store, existing_names)
        existing_names.add(new_name.lower())
        print(f"  {pdf.name}")
        print(f"    -> {new_name}")
        planned.append((pdf, new_name))

    to_rename = [(p, n) for p, n in planned if n]
    skipped   = len(planned) - len(to_rename)

    print()
    print(f"Ready to rename {len(to_rename)} file(s). {skipped} will be skipped.")
    print()

    confirm = input("Proceed with renaming? (y/n): ").strip().lower()
    if confirm != "y":
        print("Cancelled. No files were renamed.")
        input("\nPress Enter to exit...")
        return

    renamed = 0
    for pdf_path, new_name in to_rename:
        try:
            pdf_path.rename(pdf_path.parent / new_name)
            print(f"  Renamed: {pdf_path.name} -> {new_name}")
            renamed += 1
        except Exception as e:
            print(f"  Failed to rename {pdf_path.name}: {e}")

    print()
    print(f"Done. {renamed} file(s) renamed, {skipped} skipped.")
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()