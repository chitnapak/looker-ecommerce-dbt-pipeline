with source as (
    select * from {{ source('thelook', 'inventory_items') }}
)

select
    id as inventory_item_id,
    product_id,
    cast(created_at as timestamp) as created_at,
    cast(sold_at as timestamp) as sold_at,
    cost,
    product_category,
    product_name,
    product_brand,
    product_retail_price,
    product_department,
    product_sku,
    product_distribution_center_id as product_dc_id
from source
