'''
    This code checks if Ollama is installed, and if not, it downloads and runs the installer. It then starts the Ollama server in the background and pulls the llama3.2-vision model if it's not already available.

    Seongjun Yoo
'''
import os
import sys
import time
import subprocess
import urllib.request
from pathlib import Path
import requests

OLLAMA_MODEL = "qwen2.5vl:7b-q4_k_m"
OLLAMA_INSTALLER = "https://ollama.com/download/OllamaSetup.exe"

def ollama_installed() -> bool:
    for path_dir in os.environ.get("PATH", "").split(os.pathsep):
        if Path(path_dir, "ollama.exe").exists():
            return True
    # Check default install location
    local_app = os.environ.get("LOCALAPPDATA", "")
    if local_app and Path(local_app, "Programs", "Ollama", "ollama.exe").exists():
        return True
    return False

def get_ollama_exe() -> str:
    """Return the full path to ollama.exe."""
    for path_dir in os.environ.get("PATH", "").split(os.pathsep):
        candidate = Path(path_dir, "ollama.exe")
        if candidate.exists():
            return str(candidate)
    local_app = os.environ.get("LOCALAPPDATA", "")
    if local_app:
        candidate = Path(local_app, "Programs", "Ollama", "ollama.exe")
        if candidate.exists():
            return str(candidate)
    return "ollama"  # Fallback, hope it's on PATH

def download_ollama():
    """Download and run the Ollama installer."""
    print("Ollama not found. Downloading installer (~150MB)...")
    installer_path = Path(os.environ.get("TEMP", "."), "OllamaSetup.exe")

    try:
        def progress(count, block_size, total_size):
            percent = int(count * block_size * 100 / total_size)
            percent = min(percent, 100)
            print(f"\r  Downloading... {percent}%", end="", flush=True)

        urllib.request.urlretrieve(OLLAMA_INSTALLER, installer_path, reporthook=progress)
        print("\n  Download complete. Running installer...")
        print("  Please follow the Ollama setup wizard, then return here.")
        print()

        subprocess.run([str(installer_path), "/silent"], check=True)
        print("  Ollama installed successfully.")

    except Exception as e:
        print(f"\n  Failed to download/install Ollama automatically: {e}")
        print(f"  Please install manually from: https://ollama.com")
        input("\nPress Enter to exit...")
        sys.exit(1)

def is_ollama_running() -> bool:
    try:
        requests.get("http://localhost:11434", timeout=3)
        return True
    except Exception:
        return False

def start_ollama():
    print("Starting Ollama in the background...")
    ollama_exe = get_ollama_exe()
    try:
        subprocess.Popen(
            [ollama_exe, "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        )
        
        # Wait up to 15 seconds for it to become ready
        for i in range(15):
            time.sleep(1)
            if is_ollama_running():
                print("  Ollama is ready.\n")
                return
        print("  Ollama is taking longer than expected to start...")
        print("  Waiting a bit more...")
        time.sleep(5)
        if not is_ollama_running():
            print("  Could not confirm Ollama started. Trying to continue anyway...")
    except Exception as e:
        print(f"  Failed to start Ollama: {e}")
        print("  Please start Ollama manually and try again.")
        input("\nPress Enter to exit...")
        sys.exit(1)

def check_model() -> bool:
    try:
        r = requests.get("http://localhost:11434/api/tags", timeout=5)
        models = r.json().get("models", [])
        return any(OLLAMA_MODEL in m.get("name", "") for m in models)
    except Exception:
        return False

def pull_model():
    print(f"Downloading vision model: {OLLAMA_MODEL}")
    ollama_exe = get_ollama_exe()
    try:
        process = subprocess.Popen(
            [ollama_exe, "pull", OLLAMA_MODEL],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8"
        )
        for line in process.stdout:
            line = line.strip()
            if line:
                print(f"  {line}")
        process.wait()
        if process.returncode == 0:
            print(f"  Model ready.\n")
        else:
            print(f"  Model pull may have failed. Trying to continue...")
    except Exception as e:
        print(f"  Failed to pull model: {e}")
        input("\nPress Enter to exit...")
        sys.exit(1)


def ensure_ollama_ready():
    if not ollama_installed():
        download_ollama()
        time.sleep(3)  

    if not is_ollama_running():
        start_ollama()

    if not check_model():
        pull_model()