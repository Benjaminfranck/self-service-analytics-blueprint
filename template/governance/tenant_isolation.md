# ④ Tenant isolation (multi-tenant governance = a security control)

When many tenants share physical tables, a governance bug is a **cross-tenant data leak** — the worst
outcome in a security product. Isolation here is both correctness and security.

## The pattern (logical isolation)
- **`tenant` is the first column of every sort key** (and partition strategy) on shared tables — so
  every tenant-scoped query prunes efficiently.
- **Mandatory `WHERE tenant = :tenant`** injected by the query/semantic layer on **every** query —
  not optional, not left to the app or the agent. The agent never chooses the tenant filter.
- The semantic layer enforces it as an **access policy** (row-level): the tenant is bound from the
  authenticated session/user attributes, not from the NL question.

## Enforcement & tests
- A CI test asserts no governed query path can omit the tenant predicate.
- Row-count parity tests per tenant; a canary test that a tenant-A session cannot read tenant-B rows.
- RBAC + column-level controls for PII; mask sensitive columns by policy, not by convention.

## For the agent
- The agent operates **within** a tenant-scoped session; it cannot widen scope.
- "Across all tenants" questions (e.g. peer benchmarking) go through a **separate, explicitly-governed**
  aggregate that exposes only non-identifying, cohort-level numbers — never raw cross-tenant rows.

> Decide early (one of the article's calibration questions): your access-control posture determines
> whether you build **one agent** (broad access, max context) or **many scoped agents** (tighter, safer).
