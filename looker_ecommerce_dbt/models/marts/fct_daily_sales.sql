with order_items as (
    select * from {{ ref('stg_order_items') }}
),

inventory_items as (
    select * from {{ ref('stg_inventory_items') }}
)

select
    date(oi.created_at) as sale_date,
    ii.product_category as product_category,
    ii.product_brand as product_brand,
    ii.product_department as product_department,
    count(distinct oi.order_id) as total_orders,
    count(distinct oi.order_item_id) as total_items_sold,
    sum(oi.sale_price) as total_revenue,
    sum(ii.cost) as total_cost,
    sum(oi.sale_price - ii.cost) as total_profit,
    count(distinct case when oi.status = 'Returned' then oi.order_item_id end) as total_returns
from order_items oi
left join inventory_items ii
    on oi.inventory_item_id = ii.inventory_item_id
group by 1, 2, 3, 4
