# CloudPulse Cloud Infrastructure and Disaster Recovery Guide

## 1. Cloud Architecture Overview
CloudPulse production architecture operates across an active-passive multi-region topology hosted on Amazon Web Services (AWS):
- **Primary Region**: `us-east-1` (N. Virginia) - handles 100% of primary read-write workloads.
- **Secondary DR Region**: `us-west-2` (Oregon) - warm standby environment synchronized via cross-region read replicas and automated storage replication.

## 2. Container Orchestration & Autoscaling
- **Kubernetes (EKS)**:
  - Microservices run in managed Kubernetes (Amazon EKS) version 1.30+.
  - Nodes use AWS Graviton ARM64 compute instances (`c7g.2xlarge`) for power efficiency and cost optimization.
- **Horizontal Pod Autoscaling (HPA)**:
  - Target CPU utilization threshold is set to **70%**.
  - Target memory utilization threshold is set to **80%**.
  - Minimum pod replica count is 3 per service across distinct Availability Zones (AZs) for high availability.
  - Maximum pod replica count during peak flash sales is 60 replicas.

## 3. Disaster Recovery (DR) Objectives
- **Recovery Time Objective (RTO)**:
  - The target maximum acceptable downtime during regional failover is **15 minutes**.
  - Automated Route53 DNS health checks trigger regional traffic rerouting if the primary region fails health checks for 3 consecutive 30-second cycles.
- **Recovery Point Objective (RPO)**:
  - The maximum allowable data loss window is **5 minutes**.
  - Aurora PostgreSQL global databases maintain asynchronous continuous replication with replica lag monitored strictly under 1,000 milliseconds.

## 4. Backup Strategies and Storage Lifecycle
- **Database Snapshots**:
  - Full automated snapshot backups are created daily at **01:00 UTC**.
  - Transaction logs (WAL) are streamed continuously every 5 minutes to S3 Glacier Instant Retrieval.
  - Database daily snapshots are retained for **35 days**.
- **Cold Storage Archival**:
  - Raw system metrics and diagnostic logs older than 90 days are transitioned automatically to S3 Glacier Deep Archive.

