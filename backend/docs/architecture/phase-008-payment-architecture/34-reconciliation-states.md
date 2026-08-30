# AGENTPAY — 34: 9 Reconciliation Discrepancy Classifications

## 1. Discrepancy Taxonomy

1. `MATCHED`: Internal and Razorpay settlement amounts and statuses match 100%.
2. `MISSING_INTERNAL`: Razorpay record exists, missing from internal DB.
3. `MISSING_PROVIDER`: Internal record exists in `EXECUTED`, missing from Razorpay.
4. `AMOUNT_MISMATCH`: Internal settlement amount differs from Razorpay amount.
5. `STATUS_MISMATCH`: Internal status (`FAILED`) differs from Razorpay (`captured`).
6. `CURRENCY_MISMATCH`: Currency code discrepancy.
7. `DUPLICATE`: Multiple Razorpay payments match a single internal intent.
8. `UNKNOWN`: Unresolved discrepancy pending investigation.
9. `RESOLVED`: Discrepancy manually resolved by security operations operator.
