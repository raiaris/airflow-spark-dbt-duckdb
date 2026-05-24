with source_data as (
    select * from iceberg_scan('/warehouse/default/fraud_raw')
)

select
    cast(timestamp as bigint) as timestamp,
    sending_address,
    receiving_address,
    cast(NULLIF(amount, 'none') as double) as amount,
    transaction_type,
    location_region,
    ip_prefix,
    cast(login_frequency as int)  as login_frequency,
    cast(session_duration as int) as session_duration,
    purchase_pattern,
    age_group,
    risk_score,
    anomaly,
    year,
    month,
    day,
    dagrun_id
from source_data
