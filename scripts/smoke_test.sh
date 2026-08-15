#!/usr/bin/env sh
set -eu
curl --fail --silent http://localhost:8000/health
curl --fail --silent http://localhost:8000/ready
curl --fail --silent -H 'content-type: application/json' -d '{"customer_id":"CUST-10001","tenure_months":13,"monthly_spend":79.99,"total_spend":1020.5,"support_tickets":4,"login_frequency":3,"subscription_plan":"premium","payment_failures":2,"days_since_last_login":15,"usage_score":0.42,"contract_type":"monthly","region":"south"}' http://localhost:8000/predict
