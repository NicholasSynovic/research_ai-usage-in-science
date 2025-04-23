#!/bin/bash

# find bulk_pdfs -name "*.pdf" -exec echo "Hello {}" \;

find author-agreement-docs -name "*.pdf" -exec python automatedAnalysis.py -i {} -m "qwq" -p "Do the author's use deep learning methods in their paper?" -t 600 --prediction-tokens 2000 --context-tokens 38000 >> usesDL.txt \;

# ls author-agreement-docs/*.pdf | xargs -I % python automatedAnalysis.py -i % -m "qwq" -p "Do the author's use pre-trained deep learning models in their paper?" -t 600 --prediction-tokens 2000 --context-tokens 38000 >> usesPTMs.txt
# ls author-agreement-docs/*.pdf | xargs -I % python automatedAnalysis.py -i % -m "qwq" -p "What pre-trained deep learning models in their paper?" -s "Respond as a list of deep learning model names" -t 600 --prediction-tokens 4000 --context-tokens 36000 >> ptmsUsed.txt
# ls author-agreement-docs/*.pdf | xargs -I % python automatedAnalysis.py -i % -m "qwq" -p "How are pre-trained models reused?" -s "Respond as succinctly as possible" -t 600 --prediction-tokens 4000 --context-tokens 36000 >> ptmReuse.txt
