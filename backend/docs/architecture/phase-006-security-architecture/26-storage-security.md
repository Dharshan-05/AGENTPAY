# AGENTPAY — 26: Object Storage Buckets & Signed Pre-Shared URLs

## 1. Storage Security Rules

* **Private Buckets**: Object storage buckets (S3 / MinIO) for receipt images and audit archives are strictly private. Public access is disabled.
* **Signed URLs**: Access to private files requires short-lived pre-signed URLs with a 15-minute expiration window.
* **Tenant Prefix**: File keys enforce tenant prefix paths: `s3://agentpay-vault/<tenant_id>/<file_key>`.
