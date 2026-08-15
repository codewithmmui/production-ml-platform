import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def generate_churn_data(rows: int = 50_000, seed: int = 42, drift: bool = False) -> pd.DataFrame:
    if rows < 100:
        raise ValueError("rows must be at least 100")
    rng = np.random.default_rng(seed)
    tenure = rng.integers(1, 73, rows)
    plan = rng.choice(["basic", "standard", "premium"], rows, p=[0.42, 0.38, 0.20])
    contract = rng.choice(["monthly", "annual", "two_year"], rows, p=[0.58, 0.30, 0.12])
    region = rng.choice(["north", "south", "east", "west"], rows)
    monthly = np.maximum(15, rng.normal(68 if not drift else 82, 24, rows)).round(2)
    tickets = rng.poisson(1.5 if not drift else 2.6, rows)
    logins = rng.poisson(11 if not drift else 7, rows)
    failures = rng.binomial(4, 0.11 if not drift else 0.22, rows)
    inactive = np.maximum(0, rng.gamma(2 if not drift else 3, 5, rows)).round().astype(int)
    usage = np.clip(rng.beta(4 if not drift else 2.7, 2.3, rows), 0, 1).round(4)
    total = np.maximum(0, monthly * tenure * rng.normal(0.96, 0.07, rows)).round(2)
    logit = (
        -2.0
        + failures * 1.05
        + tickets * 0.42
        - logins * 0.095
        + inactive * 0.070
        - usage * 2.85
        + monthly * 0.016
        + (contract == "monthly") * 1.45
        - tenure * 0.032
        + (plan == "premium") * 0.20
    )
    probability = 1 / (1 + np.exp(-logit))
    churned = rng.binomial(1, probability)
    frame = pd.DataFrame(
        {
            "customer_id": [f"CUST-{i:08d}" for i in range(rows)],
            "tenure_months": tenure,
            "monthly_spend": monthly,
            "total_spend": total,
            "support_tickets": tickets,
            "login_frequency": logins,
            "subscription_plan": plan,
            "payment_failures": failures,
            "days_since_last_login": inactive,
            "usage_score": usage,
            "contract_type": contract,
            "region": region,
            "churned": churned,
        }
    )
    # Deterministic, realistic sparse missingness in nullable input fields.
    for column, rate in {"monthly_spend": 0.006, "usage_score": 0.008, "region": 0.004}.items():
        frame.loc[rng.random(rows) < rate, column] = np.nan
    return frame


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate deterministic churn data")
    parser.add_argument("--rows", type=int, default=50_000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=Path, default=Path("data/raw/customers.csv"))
    parser.add_argument("--drift", action="store_true")
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    generate_churn_data(args.rows, args.seed, args.drift).to_csv(args.output, index=False)
    print(f"generated rows={args.rows} drift={args.drift} output={args.output}")


if __name__ == "__main__":
    main()
