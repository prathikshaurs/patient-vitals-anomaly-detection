-- To clean and standardize raw vitals data

with source as (
    select * from patient_vitals.vitals_raw
),

cleaned as (
    select
        subject_id,
        hadm_id,
        stay_id,
        -- Convert charttime to proper datetime
        cast(charttime as datetime)     as charttime,
        itemid,
        vital_sign,
        -- Round value to 2 decimal places
        round(value, 2)                 as value,
        -- Add a readable label for each vital sign
        case vital_sign
            when 'heart_rate'    then 'Heart Rate (BPM)'
            when 'spo2'          then 'Oxygen Saturation (%)'
            when 'systolic_bp'   then 'Systolic BP (mmHg)'
            when 'diastolic_bp'  then 'Diastolic BP (mmHg)'
            else vital_sign
        end                             as vital_sign_label,
        -- Flag readings outside normal ranges
        case
            when vital_sign = 'heart_rate'   and (value < 20  or value > 300) then 1
            when vital_sign = 'spo2'         and (value < 0   or value > 100) then 1
            when vital_sign = 'systolic_bp'  and (value < 0   or value > 300) then 1
            when vital_sign = 'diastolic_bp' and (value < 0   or value > 200) then 1
            else 0
        end                             as is_physiologic_violation
    from source
    -- Exclude null values
    where value is not null
)

select * from cleaned