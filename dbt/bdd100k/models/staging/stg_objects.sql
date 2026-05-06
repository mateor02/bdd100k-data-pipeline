with source as (
    select * from {{ source('bdd100k_labels', 'objects')  }}
),

cleaned as (
    select
        name as clip_id,
        case
            when category = 'bike' then 'bicycle'
            when category = 'motor' then 'motorcycle'
            else category
        end as object_category,
        id as object_id,
        occluded as is_occluded,
        truncated as is_truncated,
        trafficlightcolor as traffic_light_color,
        x1 as bbox_x_min,
        y1 as bbox_y_min,
        x2 as bbox_x_max,
        y2 as bbox_y_max
    from source
)

select * from cleaned