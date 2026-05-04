-- For final summary table joining features with anomaly flags

with features as (
    select * from {{ ref('int_vitals_features') }}
),

anomalies as (
    select
        subject_id,
        stay_id,
        charttime,
        vital_sign,
        anomaly_flag,
        anomaly_score,
        shap_value,
        shap_rolling_mean_3,
        shap_rolling_std_3,
        shap_lag_1,
        shap_rate_of_change
    from patient_vitals.anomaly_results
),

final as (
    select
        f.subject_id,
        f.hadm_id,
        f.stay_id,
        f.charttime,
        f.vital_sign,
        f.vital_sign_label,
        f.value,
        f.is_physiologic_violation,
        f.rolling_mean_3,
        f.rolling_std_3,
        f.lag_1,
        f.rate_of_change,
        a.anomaly_flag,
        a.anomaly_score,
        a.shap_value,
        a.shap_rolling_mean_3,
        a.shap_rolling_std_3,
        a.shap_lag_1,
        a.shap_rate_of_change,
        -- Severity label based on anomaly score
        case
            when a.anomaly_flag = 1 and abs(a.anomaly_score) > 0.1 then 'High'
            when a.anomaly_flag = 1 and abs(a.anomaly_score) > 0.05 then 'Medium'
            when a.anomaly_flag = 1 then 'Low'
            else 'Normal'
        end as severity
    from features f
    left join anomalies a
        on  f.subject_id = a.subject_id
        and f.stay_id    = a.stay_id
        and f.charttime  = a.charttime
        and f.vital_sign = a.vital_sign
)

select * from final