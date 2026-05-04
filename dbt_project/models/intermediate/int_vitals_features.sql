-- To feature engineering on cleaned vitals using SQL window functions

with stg as (
    select * from {{ ref('stg_vitals') }}
),

features as (
    select
        subject_id,
        hadm_id,
        stay_id,
        charttime,
        vital_sign,
        vital_sign_label,
        value,
        is_physiologic_violation,

        -- Rolling average of last 3 readings per patient per vital sign
        round(avg(value) over (
            partition by subject_id, stay_id, vital_sign
            order by charttime
            rows between 2 preceding and current row
        ), 2) as rolling_mean_3,

        -- Rolling standard deviation of last 3 readings
        round(stddev(value) over (
            partition by subject_id, stay_id, vital_sign
            order by charttime
            rows between 2 preceding and current row
        ), 2) as rolling_std_3,

        -- Previous reading value
        lag(value, 1) over (
            partition by subject_id, stay_id, vital_sign
            order by charttime
        ) as lag_1,

        -- Rate of change since last reading
        round(value - lag(value, 1) over (
            partition by subject_id, stay_id, vital_sign
            order by charttime
        ), 2) as rate_of_change

    from stg
)

select * from features