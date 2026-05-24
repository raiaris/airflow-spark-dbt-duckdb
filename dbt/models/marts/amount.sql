with base as (
    select
        location_region,
        avg(try_cast(risk_score as double)) as avg_risk_score
    from {{ ref('stg_fraud__transactions') }}
    where location_region is not null
    group by location_region
)

select
    location_region,
    round(avg_risk_score, 4) as avg_risk_score
from base
order by avg_risk_score desc
