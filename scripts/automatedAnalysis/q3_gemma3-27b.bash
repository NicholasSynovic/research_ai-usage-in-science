#!/bin/bash

$(OLLAMA_DEBUG="1" ollama serve 2>&1 | tee q3_gemma3-27b_ollama.log) &

find $(dirname "$0")/pdfs -name "*.pdf" -exec python automatedAnalysis.py -i {} -m "gemma3:27b" -p "What pre-trained deep learning models are reused in this paper?" -t 600 --prediction-tokens 2000 --context-tokens 124000 >> q3_gemma3-27b.txt \;
