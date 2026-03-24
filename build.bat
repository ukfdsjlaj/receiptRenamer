@echo off
echo ============================================
echo   Receipt Renamer - Build to EXE
echo ============================================
echo.

echo Step 1: Installing required packages...
pip install pymupdf pillow requests pyinstaller
echo.

echo Step 2: Building executable...
pyinstaller --onefile --console --name "ReceiptRenamer" rename_receipts.py
echo.

echo ============================================
if exist dist\ReceiptRenamer.exe (
    echo   Build successful!
    echo   Your exe is at: dist\ReceiptRenamer.exe
    echo.
    echo   Just run ReceiptRenamer.exe - it will:
    echo     - Install Ollama automatically if needed
    echo     - Download the vision model if needed
    echo     - Start Ollama in the background automatically
    echo     - Ask for your receipts folder on first run
) else (
    echo   Build may have failed. Check the output above for errors.
)
echo ============================================
echo.
pause
