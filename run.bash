#!/bin/bash

aius search --journal plos
aius search --journal nature
aius extract-documents
aius openalex --email nsynovic@luc.edu
aius filter
