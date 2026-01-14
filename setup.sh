#!/bin/bash
pip install -r requirements.txt
ollama serve &
ollama pull phi3:mini
ollama pull qwen2.5
