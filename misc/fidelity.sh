#!/bin/sh

python src/read_fidelity_csv.py --input private/History_for_Account_#########.csv  --output out.csv -l 3 -m data/fidelity_mapper.csv

