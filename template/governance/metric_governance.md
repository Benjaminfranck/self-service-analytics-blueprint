# ④ Metric governance

Governance is what makes the *same question* return the *same number* for everyone — and lets you
prove why. Without **teeth**, it decays back to the "forty candidates" problem within weeks.

## The three teeth (governance without enforcement decays)
1. **Tooling** — the agent is structurally routed to the governed layer first (the router skill).
2. **CI** — changes that bypass governance fail review (paired-doc gate, contract enforcement).
3. **Mandate** — downstream teams build on the governed layer or document why not.

## Certification tiers
| Tier | Meaning | Badge / flag |
|---|---|---|
| **certified / gold** | reviewed, owned, single-source-of-truth | `meta: {certified: true, tier: gold}` + agent prefers it |
| **standard** | usable, not yet certified | no badge |
| **experimental / ungoverned** | ad-hoc, self-serve | `public: false` / clearly marked; agent warns |

## Ownership, versioning, anti-sprawl
- Every metric/model has an **owner** (`meta.owner`) and lives in an access **group** (`access: public|protected|private`).
- **Canonical** datasets marked `meta: {canonical: true}`; near-duplicates get a **`deprecation_date`** (consumers warned → promote to error).
- **Contracts** (`contract: {enforced: true}`) preflight column names/types; a contracted model can't be deleted before its deprecation date.
- **One definition, every surface.** Distribute via the semantic-layer API / MCP so dashboards, Slack, IDE, and the agent return the same number. Avoid semantic-layer *sprawl* (multiple competing layers → trust collapses).

## Governed self-serve (resolving the core tension)
Democratize dashboards over a **catalog of certified metrics** users *compose* but can't silently
redefine; ad-hoc metrics are clearly marked uncertified. Self-serve over a governed metrics layer —
never over raw SQL. (This is how you get "build your own dashboard" without metric sprawl.)

## Tunable-but-governed scores (security-specific)
Risk/severity scores ship certified defaults but allow scoped, **tracked** customization, with a
mandatory **"why" trace** ("downgraded Critical→Medium: not internet-facing + compensating control +
EPSS 0.02"). Watch the tradeoff: too much per-customer re-weighting and cross-tenant **peer
benchmarking** stops being comparable.
