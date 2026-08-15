# ML lifecycle

Data is generated/ingested, validated, transformed, split, trained, compared on validation PR-AUC, refit, and evaluated once on test. MLflow captures lineage. Absolute thresholds reject unsafe candidates; a challenger must additionally exceed champion ROC-AUC by the configured delta. Drift can trigger evaluation, never automatic blind replacement. Registry aliases express candidate, staging, production, and archived states.
