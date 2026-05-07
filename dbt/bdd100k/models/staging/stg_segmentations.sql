with source as (
    select * from {{ source('bdd100k_labels', 'segmentations') }}
),

renamed as (
    select
        name as clip_id,
        category as segmentation_type,
        id as segmentation_id,
        direction as lane_direction,
        style as lane_style
    from source
)

select * from renamed