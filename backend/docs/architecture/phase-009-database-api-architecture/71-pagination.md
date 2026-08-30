# AGENTPAY — 71: Cursor-Based Opaque Pagination Specification

## 1. Cursor Pagination Protocol

List endpoints support cursor pagination using opaque base64 cursor tokens:

```
GET /api/v1/payments?limit=20&cursor=eyJjcmVhdGVkX2F0IjoiMjAyNi0wOC0yNFQyMjowMDowMFoiLCJpZCI6InBheV8xMjMifQ==
```

### Pagination Response Metadata

```json
{
  "data": [...],
  "pagination": {
    "limit": 20,
    "next_cursor": "eyJjcmVhdGVkX2F0IjoiMjAyNi0wOC0yNFQyMTowMDowMFoiLCJpZCI6InBheV80NTYifQ==",
    "has_more": true
  }
}
```
