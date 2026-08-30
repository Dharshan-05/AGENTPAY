# AGENTPAY — 59: Phase Scope Partitioning (Hackathon MVP vs Production Scale)

## 1. MVP vs Future Scope Matrix

| Capability Category | Phase 010 Hackathon MVP | Post-Hackathon Production Scale |
| :--- | :--- | :--- |
| **Monorepo Workspace** | PNPM Workspaces + Turborepo | Remote Build Caching (Turborepo Cloud) |
| **Database Engine** | Local Containerized PostgreSQL 15 | Multi-AZ AWS RDS PostgreSQL / Aurora |
| **Caching / Locks** | Single Redis Container | Multi-Node Redis Cluster + Sentinel |
| **Agent Execution** | Python FastAPI Microservice | Kubernetes Pod Autoscaling + Ray Cluster |
| **CI/CD Pipeline** | GitHub Actions Workflow | GitOps ArgoCD + Automated Kubernetes Deployment |
