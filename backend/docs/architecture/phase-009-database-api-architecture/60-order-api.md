# AGENTPAY — 60: Order Management REST API Endpoints Specification

## 1. Order REST Endpoints

* `POST /api/v1/orders`: Create new purchase order header & line items.
* `GET /api/v1/orders/{order_id}`: Retrieve purchase order details.
* `GET /api/v1/orders`: List tenant orders with status filter & pagination.
* `POST /api/v1/orders/{order_id}/cancel`: Cancel unfulfilled order.
