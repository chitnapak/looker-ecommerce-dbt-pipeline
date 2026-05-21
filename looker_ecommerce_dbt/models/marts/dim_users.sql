with users as (
    select * from {{ ref('stg_users') }}
)

select
    user_id,
    first_name,
    last_name,
    full_name,
    email,
    age,
    gender,
    state,
    city,
    country,
    latitude,
    longitude,
    traffic_source,
    created_at,
    -- Extract cohort year and month for user analytics
    format_timestamp('%Y-%m', created_at) as cohort_month
from users
