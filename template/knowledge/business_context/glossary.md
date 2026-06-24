<!-- ⑤ BUSINESS-CONTEXT KB — resolves what the user MEANT, not just what they asked.
     RULE: store metric IDs, NEVER live metric VALUES — resolve numbers via the semantic layer
     at answer time, so the agent never quotes a stale figure from a months-old doc. -->

# Glossary — canonical terms → governed definitions

| Term / alias | Means | Resolves to (metric ID / entity) | Owner |
|---|---|---|---|
| "critical finding", "criticals" | open finding with normalized severity = critical | metric `open_critical_findings` | security-analytics |
| "MTTR", "time to fix" | mean hours from detection to remediation | metric `mttr_hours` | security-analytics |
| "SLA compliance" (criticals) | % criticals remediated within 72h | metric `critical_remediation_sla_rate` | security-analytics |
| "exploitable" | KEV-listed or EPSS-high | dimension `finding.is_exploitable` | security-analytics |
| "exposure", "internet-facing risk" | open findings on `is_internet_facing` assets | `open_critical_findings` filtered on asset.is_internet_facing | security-analytics |
| "coverage gap" | assets missing a required control (EDR/agent) | pattern: assets LEFT JOIN control | sec-ops |
| "the Q2 hardening push" | a specific program — see initiative | `business_context/initiatives/INIT-Q2-HARDENING.md` | sec-ops |

## Acronyms
- **KEV** — CISA Known Exploited Vulnerabilities. **EPSS** — Exploit Prediction Scoring System.
- **CTEM** — Continuous Threat Exposure Management. **EDR** — Endpoint Detection & Response.

## Disambiguation rules (clarify before querying)
- "active assets" — confirm: assets seen in last 30d, or non-decommissioned? Default = non-decommissioned (`dim_assets`).
- "risk" — a governed board-level risk score ≠ raw finding counts. Confirm which.
- Two teams may use "critical" differently — default to the normalized enum; confirm if the asker owns a tuned model.
