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
    image_b64 = file_to_base64(file_path)

    # If the frequently used card list is given, give it to AI
    hint_section = ""
    if known_cards:
        cards_string = ", ".join(known_cards)
        hint_section = f"""
CRITICAL HINT FOR CARD NUMBER:
Those are the 4 digits of card that are frequently used: {cards_string}. 
If you find a 4 digit number on the receipt that matches one of these, prioritize that as the "card" value.
"""

    # Prompt to be given to the AI
    prompt = f"""You are an expert data extraction assistant. Analyze the provided receipt image and extract the following information into a strict JSON object.

Fields to extract:
1. "card": The final 4 digits of the payment card. If cash was used or it cannot be found, return 0000.
2. "date": The date of the transaction. You MUST standardize this to "YYYY-MM-DD" format. If the receipt shows a 2-digit year (e.g., DD/MM/YY), you must convert it to a 4-digit year by adding "20" to the front (e.g., "23" becomes "2023").
3. "store": The name of the business or store. Keep it concise (e.g., "Walmart", not "Walmart Supercenter #1234").
4. "totalAmount": The final total amount paid. Return as a number (e.g., 12.99). Do not include currency symbols like "$".

CRITICAL RULES:
- Respond ONLY with the raw JSON object.
- Do not wrap the response in markdown blocks (e.g., do not use ```json).
- Do not include any greetings, explanations, or conversational text.
- If a specific piece of information cannot be found on the receipt, use null for that field.


{hint_section}
Respond ONLY with a JSON object in this exact format, nothing else:
{{
  "card": "1234",
  "date": "YYYY-MM-DD",
  "store": "StoreName",
  "totalAmount": 24.50
}}
"""

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
        print(f"  Could not parse response for {file_path.name}")
        return {"card": None, "date": None, "store": None}
    except requests.exceptions.Timeout:
        print(f"  Timed out on {file_path.name} — try again")
        return {"card": None, "date": None, "store": None}
    except Exception as e:
        print(f"  Error processing {file_path.name}: {e}")
        return {"card": None, "date": None, "store": None}
    
def stripedFilename(name: str) -> str:
    return re.sub(r'[<>:"/\\|?*]', "", name).strip()

def build_new_filename(card: str, date: str, store: str, existing: set, ext: str) -> str:
    clean_date = str(date).replace("/", "-").replace("\\", "-")
    base = f"{stripedFilename(card)} {clean_date} {stripedFilename(store)}"
    
    # Keep the extension
    candidate = base + ext
    counter = 1
    while candidate.lower() in existing:
        candidate = f"{base} {counter}{ext}"
        counter += 1
    return candidate