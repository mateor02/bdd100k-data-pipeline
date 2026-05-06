with source as (
    select * from {{ source('bdd100k_labels', 'clips') }}
),

renamed as (
    select
        name as clip_id,
        timeofday as time_of_day,
        weather,
        scene as scene_type
    from source
)

select * from renamed


