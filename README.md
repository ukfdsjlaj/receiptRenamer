# receiptRenamer

## Objective
Using Ollama, rename receipt pdf to "{card_number} {date} {store_Name}"

## System Requirement
This runs on device AI, meaning it requires a powerful hardware enough to run AI locally.
At least 16gb of DRAM and a dedicated GPU with 6gb VRAM is recommended.

## How to download / Use
1. Direct to dist folder and download the receiptRenamer application (exe).
2. Run the exe file.
3. CMD will pop up and download Ollama and llama AI model. This step takes 5-10 minutes, maybe longer depending on network.If the installation is successful skip to step 6.
4. If step 3 fails, google Ollama and download it manually.
5. Once Ollama is downloaded, pull llama 3.2. Open Command Prompt and type <code>ollama pull llama3.2-vision</code>.
6. Once everything is donwloaded, the application would prompt the folder location. Simply copy and paste the folder address of the desired folder.
7. Once rename is completed, it would ask to finalize the file name or to discard the change. Press y to confirm the change.
