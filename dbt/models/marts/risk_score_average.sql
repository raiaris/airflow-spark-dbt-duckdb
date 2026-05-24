with sales as (
    select
        receiving_address,
        amount,
        timestamp
    from {{ ref('stg_fraud__transactions') }}
    where transaction_type = 'sale'
      and amount is not null
),

most_recent_per_address as (
    select
        receiving_address,
        amount,
        timestamp,
        row_number() over (
            partition by receiving_address
            order by timestamp desc
        ) as rn
    from sales
)

select
    receiving_address,
    amount,
    timestamp
from most_recent_per_address
where rn = 1
order by amount desc
limit 3
