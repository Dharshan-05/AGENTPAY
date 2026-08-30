# AGENTPAY — 14: `order_items` Relational Table Schema & Line Total Constraints

## 1. `order_items` Table SQL DDL

```sql
CREATE TABLE order_items (
    item_id VARCHAR(64) PRIMARY KEY,
    order_id VARCHAR(64) NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
    product_id VARCHAR(64) NOT NULL,
    description TEXT NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(18,4) NOT NULL CHECK (unit_price >= 0),
    tax NUMERIC(18,4) NOT NULL DEFAULT 0 CHECK (tax >= 0),
    discount NUMERIC(18,4) NOT NULL DEFAULT 0 CHECK (discount >= 0),
    line_total NUMERIC(18,4) NOT NULL CHECK (line_total >= 0),
    currency VARCHAR(3) NOT NULL DEFAULT 'INR',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_item_total CHECK (line_total = ((quantity * unit_price) + tax - discount))
);

CREATE INDEX idx_order_items_order ON order_items(order_id);
```
