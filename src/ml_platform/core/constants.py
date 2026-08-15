TARGET = "churned"
ENTITY = "customer_id"
CATEGORICAL_FEATURES = ["subscription_plan", "contract_type", "region"]
NUMERIC_FEATURES = [
    "tenure_months",
    "monthly_spend",
    "total_spend",
    "support_tickets",
    "login_frequency",
    "payment_failures",
    "days_since_last_login",
    "usage_score",
]
RAW_FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES
