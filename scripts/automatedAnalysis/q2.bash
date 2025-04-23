#!/bin/bash

source $(dirname "$0")/optparse.bash
optparse.define short=d long=directory desc="The directory of PDFs to process" variable=pdf_dir
optparse.define short=o long=output desc="The output file" variable=output_file default=q2.txt
source $( optparse.build )

$(OLLAMA_DEBUG="1" ollama serve 2>&1 | tee q2_ollama.log) &
find $pdf_dir -name "*.pdf" -exec python automatedAnalysis.py -i {} -m "qwq" -p "Do the author's use pre-trained deep learning models in their paper?" -t 600 --prediction-tokens 2000 --context-tokens 38000 >> $output_file \;
