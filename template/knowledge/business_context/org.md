<!-- ⑤ Org structure — lets the agent resolve "who owns this", route by team, and understand
     why a question is being asked. Store roles/teams, not secrets. -->

# Organization

## Teams that consume security analytics
- **SOC analysts** — triage findings mid-incident. JTBD: "is this real, and what do I do?" → drill-down tables, fast.
- **Sec-ops / vulnerability management** — own remediation programs (e.g. the Q2 Hardening Push). JTBD: SLA/coverage/KPIs.
- **CISO** — posture & risk narrative. JTBD: one number + trend + the "why".
- **Board / audit / risk committee** — quarterly risk & financial exposure. JTBD: defensible, reproducible numbers (needs human sign-off).

## Ownership
- `fct_findings`, `dim_assets`, all `open_*` / `mttr_*` metrics → **security-analytics** (security-analytics@&lt;org&gt;).
- Coverage / asset inventory → **sec-ops**.
- Board risk score → **risk** (governed separately; do not derive from raw finding counts).

## Why this matters to the agent
Persona drives **rendering** (analyst → table; board → one number + trend) and **routing** (a coverage
question goes to sec-ops' models). The org map + initiatives let the agent answer what the user *meant*.
