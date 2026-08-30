# AGENTPAY — 32: Infinite Loop & Cost Explosion Safeguards (`max_steps`)

## 1. Hard Execution Bounds

To prevent infinite loops, runaway API costs, and token exhaustion:

* **`max_steps`**: Maximum 10 step iterations per task execution graph.
* **`max_tool_calls`**: Maximum 5 tool invocations per task.
* **`max_runtime`**: 30-second maximum runtime SLA per intent cycle.
* **`max_cost`**: Maximum ₹50 estimated API token cost per task.

Exceeding limits terminates execution, logs `ERR_LOOP_LIMIT_EXCEEDED`, and alerts the user.
