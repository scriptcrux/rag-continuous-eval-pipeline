# CloudPulse Enterprise Security and Compliance Policy

## 1. Compliance Framework Standards
CloudPulse maintains continuous compliance certifications under **SOC 2 Type II**, **ISO/IEC 27001:2022**, and **HIPAA HITECH** security rules. All infrastructure, employee accounts, and automated deployment pipelines must strictly adhere to these compliance baselines.

## 2. Authentication and Identity Management
- **Multi-Factor Authentication (MFA)**:
  - MFA is mandatory for all employee accounts, VPN gateways, cloud provider consoles (AWS/GCP), and code repositories.
  - Allowed MFA methods: Hardware security keys (FIDO2 / WebAuthn, such as YubiKey) or time-based one-time password (TOTP) authenticator apps.
  - SMS/Voice-call verification is explicitly prohibited due to SIM-swapping vulnerabilities.
- **Session Lifetimes & Idle Timeouts**:
  - Web console access sessions expire after **8 hours** maximum.
  - Inactive sessions terminate after **15 minutes** of idle time.
- **Password Complexity**:
  - Master corporate passwords must contain a minimum of 16 characters, including uppercase, lowercase, numbers, and symbols.
  - Corporate passwords must be rotated every 90 days.

## 3. Data Protection and Cryptographic Standards
- **Encryption in Transit**:
  - All external and inter-service HTTP communications must be encrypted using **TLS 1.3** (TLS 1.2 is tolerated as legacy fallback; TLS 1.0 and 1.1 are permanently disabled).
  - Weak cipher suites (e.g., RC4, 3DES, CBC mode ciphers) are strictly blocked.
- **Encryption at Rest**:
  - All database volumes, object storage buckets (S3/GCS), and persistent disk volumes must be encrypted with **AES-256** or AWS KMS Customer-Managed Keys (CMK).
  - Encryption keys must undergo automated cryptographic rotation every **365 days**.

## 4. Audit Logging and Data Retention Rules
- **Security Audit Logs**:
  - All authentication logs, administrative actions, API gateway access logs, and firewall ingress/egress logs must be forwarded in real time to the centralized immutable SIEM cluster.
  - Security audit logs must be retained for a minimum of **7 years** to satisfy SOC 2 and federal regulatory compliance audits.
- **Customer Application Data**:
  - Standard customer transactional records are retained for 3 years following account closure unless an immediate GDPR "Right to be Forgotten" deletion request is submitted.
  - GDPR deletion requests must be completed and cryptographically verified within **30 calendar days**.

