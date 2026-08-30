# AGENTPAY — 25: Frontend Security, CSP & Secure Cookie Management

## 1. Content Security Policy (CSP) & Secure Cookies

```http
Content-Security-Policy: default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self' wss://api.agentpay.io; frame-ancestors 'none';
Set-Cookie: __Host-next-auth.session-token=jwt_token_here; Secure; HttpOnly; SameSite=Strict; Path=/
```

Prevents XSS, clickjacking, and CSRF session hijacking attacks.
