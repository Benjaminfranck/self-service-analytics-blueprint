-- ① CANONICAL findings fact. Grain: one finding_id. Reads the deduped/normalized source,
-- applies the standard hygiene filter ONCE here so every downstream metric inherits it.
{{ config(materialized='table') }}

with src as (
    select * from {{ source('fabric', 'findings_normalized') }}
),
-- dedup safety net: keep the latest observation per finding (entity resolution happens upstream;
-- this guards against CDC version duplicates).
deduped as (
    select *,
        row_number() over (partition by finding_id order by ingested_at desc) as _rn
    from src
)
select
    finding_id,
    asset_id,
    ticket_id,                                    -- null ⇒ unassigned
    lower(severity)            as severity,       -- normalized enum: critical|high|medium|low
    lower(status)              as status,         -- normalized enum: open|mitigated|closed
    detected_at,
    remediated_at,
    coalesce(is_internet_facing, false) as is_internet_facing,
    coalesce(is_exploitable, false)     as is_exploitable,
    -- SLA flag used by the ratio metric (critical_remediation_sla_rate)
    case when remediated_at is not null
         and datediff('hour', detected_at, remediated_at) <= 72 then true else false end as remediated_within_sla
from deduped
where _rn = 1
  and coalesce(is_suppressed, false) = false      -- STANDARD HYGIENE FILTER (documented in reference/findings.md)
