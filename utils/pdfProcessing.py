'''
    This module contains the primary logic for processing PDF receipts, extracting key information using the Ollama API, and generat new filenames based on the extracted data.

    Seongjun Yoo
'''

import re
import json
import base64
from pathlib import Path
import requests
import fitz  # PyMuPDF
from utils.ollamaSetup import OLLAMA_MODEL

OLLAMA_URL = "http://localhost:11434/api/generate"

def file_to_base64(file_path: Path) -> str:
    ext = file_path.suffix.lower()
    
    # If it's a PDF, extract the first page like before
    if ext == ".pdf":
        doc = fitz.open(str(file_path))
        page = doc[0]
        pix = page.get_pixmap(dpi=200)
        img_bytes = pix.tobytes("jpeg")
        doc.close()
        return base64.b64encode(img_bytes).decode("utf-8")
        
    # If it's an image, just read the raw file directly!
    elif ext in [".jpg", ".jpeg", ".png"]:
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    else:
        raise ValueError(f"Unsupported file format: {ext}")

def extract_receipt_info(file_path: Path, known_cards: list = None) -> dict:
    if known_cards is None:
        known_cards = []
        
    print(f"  Reading: {file_path.name}")
    # Call the new smart function
    image_b64 = file_to_base64(file_path)

    hint_section = ""
    if known_cards:
        cards_string = ", ".join(known_cards)
        hint_section = f"""
        CRITICAL HINT FOR CARD NUMBER:
        The payment was almost certainly made with one of these cards: {cards_string}. 
        If you see a card number on the receipt that looks visually similar to one of these, output the exact matching number from this list.
        """

        prompt = f"""Look at this receipt image and extract:
        1. The last 4 digits of the card used for payment
        2. The date of the transaction
        3. The store or business name
        {hint_section}
        Respond ONLY with a JSON object in this exact format, nothing else:
        {{
        "card": "1234",
        "date": "YYYY-MM-DD",
        "store": "StoreName"
        }}

        Rules:
        - card must be exactly the last 4 digits of the card number shown on the receipt
        - date must be in YYYY-MM-DD format
        - store should be short (1-3 words max), no special characters except hyphens
        - Replace spaces in store name with hyphens (e.g. "Tim Hortons" -> "Tim-Hortons")
        - If you cannot find any field, use null for that field"""

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "images": [image_b64],
        "stream": False,
        "format": "json"
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=120)
        response.raise_for_status()
        raw = response.json().get("response", "").strip()
        raw = re.sub(r"```json|```", "", raw).strip()
        return json.loads(raw)

    except json.JSONDecodeError:
        print(f"  Could not parse response for {pdf_path.name}")
        return {"card": None, "date": None, "store": None}
    except requests.exceptions.Timeout:
        print(f"  Timed out on {pdf_path.name} — try again")
        return {"card": None, "date": None, "store": None}
    except Exception as e:
        print(f"  Error processing {pdf_path.name}: {e}")
        return {"card": None, "date": None, "store": None}

def sanitize_filename(name: str) -> str:
    return re.sub(r'[<>:"/\\|?*]', "", name).strip()

def build_new_filename(card: str, date: str, store: str, existing: set, ext: str) -> str:
    clean_date = str(date).replace("/", "-").replace("\\", "-")
    base = f"{sanitize_filename(card)} {clean_date} {sanitize_filename(store)}"
    
    # Use the original extension (.jpg, .pdf, etc.) instead of hardcoding .pdf
    candidate = base + ext
    counter = 1
    while candidate.lower() in existing:
        candidate = f"{base} {counter}{ext}"
        counter += 1
    return candidate