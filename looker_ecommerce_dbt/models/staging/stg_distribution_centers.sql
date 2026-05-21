with source as (
    select * from {{ source('thelook', 'distribution_centers') }}
)

select
    id as distribution_center_id,
    name as center_name,
    latitude,
    longitude
from source
