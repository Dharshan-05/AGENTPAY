# AGENTPAY — 30: VPC Microsegmentation & Network Policy Rules

## 1. Network Segmentation Rules

* **Isolated Database Subnet**: PostgreSQL database and Redis edge cluster reside in private subnets with no public IP addresses or direct internet egress.
* **Kubernetes NetworkPolicies**: Pod-to-pod network traffic restricted by NetworkPolicies. Only API Gateway pods can communicate with core backend pods.
* **Restricted Outbound Egress**: Outbound egress traffic from application pods restricted to verified Razorpay API IPs (`api.razorpay.com`).
