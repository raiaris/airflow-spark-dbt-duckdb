with source_data as (
    select * from {{ source('iceberg_warehouse', 'fraud_raw') }}
)

select
    cast(timestamp as bigint) as timestamp,
    cast(sending_address as varchar) as sending_address,
    cast(receiving_address as varchar) as receiving_address,
    cast(amount as double) as amount,
    cast(transaction_type as varchar) as transaction_type,
    cast(location_region as varchar) as location_region,
    cast(ip_prefix as varchar) as ip_prefix,
    cast(login_frequency as int) as login_frequency,
    cast(session_duration as int) as session_duration,
    cast(purchase_pattern as varchar) as purchase_pattern,
    cast(age_group as varchar) as age_group,
    cast(risk_score as double) as risk_score,
    cast(anomaly as varchar) as anomaly,
    cast(year as int) as year,
    cast(month as int) as month,
    cast(day as int) as day,
    cast(dagrun_id as varchar) as dagrun_id,
    cast(execution_date as timestamp) as execution_date    
from source_data