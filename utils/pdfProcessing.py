import re
import json
import base64
from pathlib import Path
import requests
import fitz  # PyMuPDF
from utils.ollamaSetup import OLLAMA_MODEL

OLLAMA_URL = "http://localhost:11434/api/generate"

def pdf_first_page_to_base64(pdf_path: Path) -> str:
    doc = fitz.open(str(pdf_path))
    page = doc[0]
    pix = page.get_pixmap(dpi=200)
    img_bytes = pix.tobytes("jpeg")
    doc.close()
    return base64.b64encode(img_bytes).decode("utf-8")

def extract_receipt_info(pdf_path: Path) -> dict:
    print(f"  Reading: {pdf_path.name}")
    image_b64 = pdf_first_page_to_base64(pdf_path)

    prompt = """Look at this receipt image and extract:
1. The last 4 digits of the card used for payment
2. The date of the transaction
3. The store or business name

Respond ONLY with a JSON object in this exact format, nothing else:
{
  "card": "1234",
  "date": "YYYY-MM-DD",
  "store": "StoreName"
}

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

def build_new_filename(card: str, date: str, store: str, existing: set) -> str:
    base = f"{card} {date} {sanitize_filename(store)}"
    candidate = base + ".pdf"
    counter = 1
    while candidate.lower() in existing:
        candidate = f"{base} {counter}.pdf"
        counter += 1
    return candidate