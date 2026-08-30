# AGENTPAY — 57: Policy Engine & Policy Versioning REST Endpoints

## 1. Policy REST Endpoints

* `POST /api/v1/policies/versions`: Publish new immutable policy version.
* `GET /api/v1/policies/versions`: List historical tenant policy versions.
* `GET /api/v1/policies/versions/{version}`: Retrieve specific policy rules.
* `POST /api/v1/policies/versions/{version}/activate`: Set active policy version.
