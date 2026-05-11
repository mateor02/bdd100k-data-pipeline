with clip_object_counts as (
    select
        clip_id,
        count(*) as total_objects,
        sum(case when object_category = 'car' then 1 else 0 end) as total_cars,
        sum(case when object_category = 'truck' then 1 else 0 end) as total_trucks,
        sum(case when object_category = 'bus' then 1 else 0 end) as total_buses,
        sum(case when object_category = 'train' then 1 else 0 end) as total_trains,
        sum(case when object_category = 'person' then 1 else 0 end) as total_pedestrians,
        sum(case when object_category = 'rider' then 1 else 0 end) as total_cyclists,
        avg((bbox_x_max - bbox_x_min) * (bbox_y_max - bbox_y_min)) as avg_bbox_area_pixels
    from {{ ref('stg_objects') }}
    group by clip_id
),

clip_segmentation_counts as (
    select
        clip_id,
        count(*) as total_segmentations,
        sum(case when segmentation_type like 'lane/%'
                 and segmentation_type not in ('lane/road curb', 'lane/crosswalk')
                 then 1 else 0 end) as total_lane_lines,
        sum(case when segmentation_type like 'area/%' then 1 else 0 end) as total_drivable_areas,
        sum(case when segmentation_type in ('lane/road curb', 'lane/crosswalk') then 1 else 0 end) as total_pedestrian_infrastructure
    from {{ ref('stg_segmentations') }}
    group by clip_id
)

select
    c.clip_id,
    c.time_of_day,
    c.weather,
    c.scene_type,
    coalesce(o.total_objects, 0) as total_objects,
    coalesce(o.total_cars, 0) as total_cars,
    coalesce(o.total_trucks, 0) as total_trucks,
    coalesce(o.total_buses, 0) as total_buses,
    coalesce(o.total_trains, 0) as total_trains,
    coalesce(o.total_pedestrians, 0) as total_pedestrians,
    coalesce(o.total_cyclists, 0) as total_cyclists,
    o.avg_bbox_area_pixels,
    coalesce(s.total_segmentations, 0) as total_segmentations,
    coalesce(s.total_lane_lines, 0) as total_lane_lines,
    coalesce(s.total_drivable_areas, 0) as total_drivable_areas,
    coalesce(s.total_pedestrian_infrastructure, 0) as total_pedestrian_infrastructure
from {{ ref('stg_clips') }} c
left join clip_object_counts o on c.clip_id = o.clip_id
left join clip_segmentation_counts s on c.clip_id = s.clip_id