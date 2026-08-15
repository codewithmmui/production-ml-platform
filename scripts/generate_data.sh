#!/usr/bin/env sh
set -eu
python -m ml_platform.data.generate --rows "${ROWS:-10000}" --seed "${SEED:-42}" --output data/raw/customers.csv
