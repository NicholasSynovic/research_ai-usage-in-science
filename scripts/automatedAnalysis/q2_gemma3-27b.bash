#!/bin/bash

$(OLLAMA_DEBUG="1" ollama serve 2>&1 | tee q2_gemma3-27b_ollama.log) &

find $(dirname "$0")/pdfs -name "*.pdf" -exec python automatedAnalysis.py -i {} -m "gemma3:27b" -p "Do the author's use pre-trained deep learning models in their paper?" -t 600 --prediction-tokens 2000 --context-tokens 124000 >> q2_gemma3-27b.txt \;
