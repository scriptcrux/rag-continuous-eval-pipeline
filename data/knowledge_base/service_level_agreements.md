# CloudPulse Service Level Agreements (SLA) Policy

## 1. Availability Guarantees
CloudPulse commits to providing enterprise customers with an Monthly Uptime Percentage commitment of at least **99.95%** across all production API services.

### Monthly Uptime Calculation Formula:
$$Uptime \% = \frac{\text{Total Minutes in Month} - \text{Unscheduled Outage Minutes}}{\text{Total Minutes in Month}} \times 100$$

Excluded from unscheduled outage minutes are:
1. Scheduled maintenance windows declared with at least 72 hours prior notice.
2. Force majeure events or third-party telecommunications carrier disruptions outside CloudPulse reasonable control.
3. Customer-originating configuration errors or unauthorized API credential floods.

## 2. Maintenance Windows
- **Standard Maintenance Schedule**:
  - Weekly maintenance windows are reserved on **Sundays between 02:00 UTC and 04:00 UTC**.
  - System upgrades during maintenance windows utilize zero-downtime rolling canary deployments to prevent customer impact.
- **Emergency Security Patching**:
  - In the event of critical zero-day vulnerabilities (CVSS score >= 9.0), emergency patches may be deployed with an expedited 4-hour advance customer notification.

## 3. Financial Service Credits for SLA Breaches
If the monthly uptime percentage drops below the guaranteed threshold of 99.95%, enterprise customers are entitled to claim financial credits applied to their subsequent billing invoice:
- **99.0% to < 99.95% uptime**: 10% credit of monthly recurring charges (MRC).
- **95.0% to < 99.0% uptime**: 25% credit of monthly recurring charges (MRC).
- **< 95.0% uptime**: 50% credit of monthly recurring charges (MRC).

### Service Credit Claims Procedure:
- Customers must submit a written credit claim ticket via the support portal within **30 calendar days** following the end of the affected billing month.
- Service credits cannot be redeemed for cash or refunded; they are exclusively applicable against future subscription invoices.

