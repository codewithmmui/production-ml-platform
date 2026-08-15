# ADR 005: Model promotion quality gates

## Context
A successful training job does not imply a safe production model.
## Decision
Require absolute ROC-AUC, PR-AUC, F1 and latency gates plus champion improvement.
## Alternatives
Accuracy-only or unconditional promotion is unsafe for imbalanced churn.
## Consequences
Promotion is auditable and conservative; thresholds need periodic business review.
