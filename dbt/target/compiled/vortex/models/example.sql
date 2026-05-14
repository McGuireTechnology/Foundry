with events as (
    select
        event_id,
        event_type,
        user_id,
        value,
        source,
        api_version,
        created_at::timestamptz as created_at
    from analytics.example_events_raw
),
daily as (
    select
        date_trunc('day', created_at) as event_day,
        event_type,
        count(*) as event_count,
        count(distinct user_id) as unique_users,
        sum(value) as total_value
    from events
    group by 1, 2
)
select *
from daily