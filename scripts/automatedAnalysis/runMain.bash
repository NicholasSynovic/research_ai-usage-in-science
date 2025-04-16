#!/bin/bash

ls *.pdf | xargs -I % python main.py -i % -m "gemma3:27b" -p "Do the author's use deep learning (including artificial neural networks) methods in their paper?" -t 120 --prediction-tokens 10 --context-tokens 64000 >> usesDL.txt
ls *.pdf | xargs -I % python main.py -i % -m "gemma3:27b" -p "Do the author's use pre-trained deep learning models in their paper?" -t 120 --prediction-tokens 10 --context-tokens 64000 >> usesPTMs.txt
