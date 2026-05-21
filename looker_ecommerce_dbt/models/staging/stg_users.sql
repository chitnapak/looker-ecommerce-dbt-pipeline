with source as (
    select * from {{ source('thelook', 'users') }}
)

select
    id as user_id,
    first_name,
    last_name,
    concat(first_name, ' ', last_name) as full_name,
    email,
    age,
    gender,
    state,
    street_address,
    postal_code,
    city,
    country,
    latitude,
    longitude,
    traffic_source,
    cast(created_at as timestamp) as created_at
from source
