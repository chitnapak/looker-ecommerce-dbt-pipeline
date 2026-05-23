with order_items as (
    select * from {{ ref('stg_order_items') }}
),

inventory_items as (
    select * from {{ ref('stg_inventory_items') }}
)

select
    oi.order_item_id,
    oi.order_id,
    oi.user_id,
    oi.product_id,
    oi.inventory_item_id,
    oi.status,
    oi.created_at,
    oi.shipped_at,
    oi.delivered_at,
    oi.returned_at,
    oi.sale_price,
    
    -- Product financial details
    ii.cost as product_cost,
    oi.sale_price - ii.cost as profit,
    
    -- Logistics & Delivery metrics (using timestamp_diff for BigQuery timestamps)
    timestamp_diff(oi.shipped_at, oi.created_at, DAY) as days_to_ship,
    timestamp_diff(oi.delivered_at, oi.shipped_at, DAY) as days_in_transit,
    timestamp_diff(oi.delivered_at, oi.created_at, DAY) as total_delivery_days,
    
    -- Status flags
    case when oi.status = 'Completed' then 1 else 0 end as is_completed,
    case when oi.status = 'Returned' then 1 else 0 end as is_returned,
    case when oi.status = 'Cancelled' then 1 else 0 end as is_cancelled
from order_items oi
left join inventory_items ii
    on oi.inventory_item_id = ii.inventory_item_id
