with order_items as (
    select * from {{ ref('stg_order_items') }}
),

products as (
    select * from {{ ref('stg_products') }}
)

select
    date(oi.created_at) as sale_date,
    p.category as product_category,
    p.brand as product_brand,
    p.department as product_department,
    count(distinct oi.order_id) as total_orders,
    count(distinct oi.order_item_id) as total_items_sold,
    sum(oi.sale_price) as total_revenue,
    sum(p.cost) as total_cost,
    sum(oi.sale_price - p.cost) as total_profit,
    count(distinct case when oi.status = 'Returned' then oi.order_item_id end) as total_returns
from order_items oi
left join products p
    on oi.product_id = p.product_id
group by 1, 2, 3, 4
