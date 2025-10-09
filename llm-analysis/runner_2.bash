INPUT="prompt_testing_dataset_plos.parquet"
MODEL="phi3:14b"
SAFE_MODEL="phi3"
PROMPT="uses-dl"

python analysis.py -i "$INPUT" -o "${SAFE_MODEL}_${PROMPT}_analysis_3.pickle" -m "$MODEL" -p "$PROMPT" --si 200 --ei 300 && \
python analysis.py -i "$INPUT" -o "${SAFE_MODEL}_${PROMPT}_analysis_4.pickle" -m "$MODEL" -p "$PROMPT" --si 300 --ei 400 && \
python analysis.py -i "$INPUT" -o "${SAFE_MODEL}_${PROMPT}_analysis_5.pickle" -m "$MODEL" -p "$PROMPT" --si 400 --ei 500 && \
python analysis.py -i "$INPUT" -o "${SAFE_MODEL}_${PROMPT}_analysis_6.pickle" -m "$MODEL" -p "$PROMPT" --si 500 --ei 600 && \
python analysis.py -i "$INPUT" -o "${SAFE_MODEL}_${PROMPT}_analysis_7.pickle" -m "$MODEL" -p "$PROMPT" --si 600 --ei 700 && \
python analysis.py -i "$INPUT" -o "${SAFE_MODEL}_${PROMPT}_analysis_8.pickle" -m "$MODEL" -p "$PROMPT" --si 700 --ei 800 && \
python analysis.py -i "$INPUT" -o "${SAFE_MODEL}_${PROMPT}_analysis_9.pickle" -m "$MODEL" -p "$PROMPT" --si 800 --ei 900 && \
python analysis.py -i "$INPUT" -o "${SAFE_MODEL}_${PROMPT}_analysis_10.pickle" -m "$MODEL" -p "$PROMPT" --si 900 --ei 1000 && \
python analysis.py -i "$INPUT" -o "${SAFE_MODEL}_${PROMPT}_analysis_11.pickle" -m "$MODEL" -p "$PROMPT" --si 1000 --ei 1100 && \
python analysis.py -i "$INPUT" -o "${SAFE_MODEL}_${PROMPT}_analysis_12.pickle" -m "$MODEL" -p "$PROMPT" --si 1100 --ei 1200 && \
python analysis.py -i "$INPUT" -o "${SAFE_MODEL}_${PROMPT}_analysis_13.pickle" -m "$MODEL" -p "$PROMPT" --si 1200 --ei 1300 && \
python analysis.py -i "$INPUT" -o "${SAFE_MODEL}_${PROMPT}_analysis_14.pickle" -m "$MODEL" -p "$PROMPT" --si 1300 --ei 1400
