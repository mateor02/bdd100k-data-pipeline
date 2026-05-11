with dataset_counts as (
    select
        weather,
        time_of_day,
        scene_type,
        count(*) as clip_count,
        sum(total_objects) as total_objects,
        avg(total_objects) as avg_objects_per_clip
    from {{ ref('fct_clip_summary')  }}
    group by weather, time_of_day, scene_type
)

select
    weather,
    time_of_day,
    scene_type,
    clip_count,
    total_objects,
    avg_objects_per_clip,
    round(clip_count * 100.0 / sum(clip_count) over (), 2) as pct_of_dataset
from dataset_counts