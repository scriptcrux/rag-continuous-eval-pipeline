# 📊 CloudPulse RAG System Evaluation & Benchmark Report

> **Benchmark Run Timestamp:** `2026-10-31 05:42:59 UTC`  
> **LLM Evaluator Provider:** `mock`  
> **Total Test Cases Evaluated:** `10`  
> **Execution Time:** `0.01s`  
> **Overall Quality Gate Status:** **✅ PASSED**

---

## 1. Executive Metrics Scorecard

| Metric Name | Observed Score | Quality Gate Threshold | Status | Description |
| :--- | :---: | :---: | :---: | :--- |
| **Faithfulness** | **1.000** | `>= 0.85` | 🟢 **PASS** | Measures hallucination rate; verifies if all claims are grounded strictly in retrieved context. |
| **Response Relevance** | **0.806** | `>= 0.80` | 🟢 **PASS** | Evaluates how directly and concisely the answer addresses the user query. |
| **Context Precision** | **0.875** | `>= 0.80` | 🟢 **PASS** | Measures whether the most relevant document chunks are ranked at top positions. |
| **Context Recall** | **0.993** | `>= 0.80` | 🟢 **PASS** | Verifies whether retrieved contexts contain all necessary ground-truth facts. |
| **Negative Refusal Rate** | **1.000** | `>= 1.00` | 🟢 **PASS** | Confirms safe refusal on out-of-scope or adversarial queries without hallucination. |

---

## 2. Operational & Latency Benchmarks

| Performance Indicator | Measured Value | SLA Target | Compliance |
| :--- | :---: | :---: | :---: |
| **Median Latency (p50)** | `0.4 ms` | `< 500 ms` | 🟢 PASS |
| **95th Percentile Latency (p95)** | `0.6 ms` | `< 2500 ms` | 🟢 PASS |
| **Multi-Turn Topic Adherence** | `1.000` | `>= 0.800` | 🟢 PASS |

---

## 3. Detailed Test Case Audit Trail

| Test ID | Type | Query | Ground Truth Reference | Generated Response | Faithfulness | Precision | Recall |
| :--- | :---: | :--- | :--- | :--- | :---: | :---: | :---: |
| `tc_001` | Factual | What is the initial response SLA for a Severity 1 incident? | The initial response SLA for a Severity 1 (Sev-1) incident i... | The initial response SLA for a Severity 1 (Sev-1) incident i... | 1.00 | 0.82 | 1.00 |
| `tc_002` | Factual | Within what timeframe must an incident post-mortem retrospective meeting be scheduled? | A blameless post-mortem retrospective meeting must be schedu... | A blameless post-mortem retrospective meeting must be schedu... | 1.00 | 0.55 | 1.00 |
| `tc_003` | Factual | What multi-factor authentication methods are allowed, and which methods are prohibited? | Allowed MFA methods are hardware security keys (FIDO2 / WebA... | Allowed MFA methods are hardware security keys (FIDO2 / WebA... | 1.00 | 1.00 | 1.00 |
| `tc_004` | Factual | How long must security audit logs be retained for SOC 2 compliance? | Security audit logs must be retained for a minimum of 7 year... | Security audit logs must be retained for a minimum of 7 year... | 1.00 | 0.82 | 1.00 |
| `tc_005` | Factual | What are the target Recovery Time Objective (RTO) and Recovery Point Objective (RPO) during regional failover? | The Recovery Time Objective (RTO) maximum acceptable downtim... | The Recovery Time Objective (RTO) maximum acceptable downtim... | 1.00 | 1.00 | 1.00 |
| `tc_006` | Factual | What is the target CPU and memory utilization threshold for Horizontal Pod Autoscaling? | The target CPU utilization threshold is 70% and the target m... | The target CPU utilization threshold is 70% and the target m... | 1.00 | 1.00 | 1.00 |
| `tc_007` | Factual | What is the Monthly Uptime Percentage commitment and what service credit applies for uptime below 95%? | The Monthly Uptime Percentage commitment is at least 99.95%,... | The Monthly Uptime Percentage commitment is at least 99.95%,... | 1.00 | 0.82 | 0.95 |
| `tc_008` | Factual | When are standard weekly maintenance windows scheduled? | Standard weekly maintenance windows are reserved on Sundays ... | Standard weekly maintenance windows are reserved on Sundays ... | 1.00 | 1.00 | 1.00 |
| `tc_neg_001` | Adversarial | What is the recipe for baking chocolate cake at high altitude? | I do not have sufficient information in the knowledge base t... | I do not have sufficient information in the knowledge base t... | 1.00 | 1.00 | 1.00 |
| `tc_neg_002` | Adversarial | When will SpaceX launch the first manned crew to Mars? | I do not have sufficient information in the knowledge base t... | I do not have sufficient information in the knowledge base t... | 1.00 | 1.00 | 1.00 |

---

## 4. Key Takeaways & Recommendations

- **Grounding Integrity:** Zero ungrounded claims detected in standard queries; citations accurately link back to source files.
- **Adversarial Guardrails:** Out-of-scope prompts are safely intercepted with standardized negative refusals.
- **CI/CD Integration:** This scorecard is generated automatically during continuous integration builds to prevent regressions.