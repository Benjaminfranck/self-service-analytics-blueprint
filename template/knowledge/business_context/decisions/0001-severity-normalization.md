# Decision 0001 — "Severity" defaults to the normalized enum, not raw scanner values

- **Status:** Accepted · **Date:** <yyyy-mm-dd> · **Owner:** security-analytics

## Context
Sources disagree on severity: CVSS v2/v3/v4 (0–10), vendor "Critical/High", EPSS (0–1), CISA KEV
membership. These are different *kinds* of statements (intrinsic severity vs exploit probability vs
known-exploited). Users say "critical" meaning different things; some customers tune their own bands.

## Decision
The canonical `severity` dimension is a **normalized enum** (`critical|high|medium|low`) produced by
a governed reconciliation transform. The
default meaning of "critical" in any query is `severity = 'critical'` on this enum. Exploitability is
a **separate** dimension (`is_exploitable`, KEV/EPSS-derived), not folded into severity.

## Consequences
- ✅ "critical" returns the same population everywhere; the reconciliation rule is explainable/auditable.
- ⚠️ If a customer uses a tuned risk band, the agent must **clarify** ("normalized severity, or your tuned model?") before answering — captured as a disambiguation rule in `glossary.md`.

## Why it's logged here
So the agent (and humans) know *why* "critical" means the enum — this is exactly the ambient context
that turns "answer what was asked" into "answer what was meant."
