#!/bin/bash

# Depends on microsoft/markitdown
# pip install 'markitdown[all]'

ls ../data/*.pdf | parallel --bar markitdown {} -o {.}.md
mdformat ../data/*.md
