#!/bin/bash

source optparse.bash
optparse.define short=d long=directory desc="The directory of PDFs to process" variable=pdf_dir
optparse.define short=o long=output desc="The output file" variable=output_file default=q3.txt
source $( optparse.build )

$(OLLAMA_DEBUG="1" ollama serve 2>&1 | tee q3_ollama.log) &
find author-agreement-docs -name "*.pdf" -exec python automatedAnalysis.py -i {} -m "qwq" -p "Do the author's use deep learning methods in their paper?" -s "Respond as a list of deep learning model names" -t 600 --prediction-tokens 2000 --context-tokens 38000 >> $output_file \;
