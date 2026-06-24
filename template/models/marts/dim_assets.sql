-- ① CANONICAL asset dimension = the golden record (entity-resolution output, upstream).
-- Grain: one row per resolved asset_id. ER/survivorship logic runs in a governed upstream transform.
{{ config(materialized='table') }}

select
    asset_id,
    hostname,
    coalesce(is_internet_facing, false) as is_internet_facing,
    environment,
    owner_id,
    business_unit
from {{ source('fabric', 'assets_golden') }}
where coalesce(is_decommissioned, false) = false
