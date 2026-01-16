#!/bin/bash
pip install -r requirements.txt
curl -fsSL https://ollama.com/install.sh | sh
ollama serve &
# ollama pull phi3:mini
# ollama pull qwen2.5
ollama pull qwen2.5:1.5b
