# Distribution — serve the system over MCP

The skills and sources of truth are **authored once** in this repo and **served everywhere** as MCP
resources, so every surface (Slack bot, IDE, dashboard tool, standalone agent session) gives the
**same answer to the same question**. On merge, CI re-publishes:
- **MCP resources** — the semantic-layer + catalog servers in `mcp.config.json` expose
  `list_metrics`, `compile_metric`, `resolve_entity`, `get_reference_doc`, `source_freshness`,
  `rank_tables`, `lineage`. The agent calls these instead of free-roaming the warehouse.
- **Plugin marketplace** — the `.claude/skills/` are packaged for IDE users.
- **Cloud-storage blobs** — hosted apps read a single synced file.

## Why MCP here
It makes the **governed layer the only interface**: the agent selects from defined metrics/entities,
so it "can only reference legitimate, governance-approved objects" — eliminating hallucinated joins
and columns. Keep everything **read-only**; the agent never mutates.

## The boring (good) fix path
Edit a markdown file → merge → auto-sync everywhere. That's the staleness defense — see the CI hook.
