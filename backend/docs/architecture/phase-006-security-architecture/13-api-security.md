# AGENTPAY — 13: API Gateway Security, BOLA/IDOR Defenses

## 1. BOLA / IDOR Protection Architecture

To prevent Broken Object-Level Authorization (BOLA / IDOR), every API resource lookup enforces a 5-part ownership check:

$$\text{Access Granted} \iff (\text{Requester User/Agent}) \land (\text{Active Session}) \land (\text{Tenant ID Match}) \land (\text{Resource Owner Match}) \land (\text{Scope Permitted})$$

---

## 2. API Gateway Security Rules

* **Payload Schema Validation**: Strictly enforced JSON Schema validation; unrecognized properties stripped.
* **Request Body Limits**: Maximum request body size capped at 100 KB.
* **Security Headers**: HSTS, CSP, X-Content-Type-Options, Frame-Options enforced on all gateway responses.
