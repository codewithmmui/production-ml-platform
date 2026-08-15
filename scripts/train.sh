#!/usr/bin/env sh
set -eu
python -m ml_platform.training.train --data data/raw/customers.csv --output artifacts "$@"
