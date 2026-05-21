with products as (
    select * from {{ ref('stg_products') }}
),

dc as (
    select * from {{ ref('stg_distribution_centers') }}
)

select
    p.product_id,
    p.cost,
    p.category,
    p.product_name,
    p.brand,
    p.retail_price,
    p.department,
    p.sku,
    p.distribution_center_id,
    dc.center_name as distribution_center_name,
    dc.latitude as dc_latitude,
    dc.longitude as dc_longitude
from products p
left join dc
    on p.distribution_center_id = dc.distribution_center_id
