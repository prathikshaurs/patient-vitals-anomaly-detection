# Patient Vitals Anomaly Detection

An end-to-end data engineering and machine learning pipeline for detecting anomalies in ICU patient vital signs, built on real clinical data from MIMIC-IV. The system ingests time-series vitals, validates data quality, engineers features, detects deterioration-like anomalies using Isolation Forest, explains results with SHAP, and orchestrates the full workflow with Apache Airflow.

---

## Overview

ICU nurses monitor multiple patients simultaneously across heart rate, blood oxygen, and blood pressure readings that update every few minutes. This pipeline automates the detection of abnormal vital sign patterns — sudden spikes, drops, or instability — that could indicate patient deterioration.

The project demonstrates a production-style data engineering workflow: raw data ingestion into MySQL, physiologic validation, SQL-based transformation with dbt, unsupervised ML anomaly detection, SHAP explainability, and full pipeline orchestration with Airflow.

---

## Pipeline Architecture
MIMIC-IV Demo (CSV)
↓
ingest.py — chunk-based ingestion into MySQL
↓
validate.py — missingness checks + physiologic threshold validation
↓
features.py — rolling mean, rolling std, lag features, rate of change
↓
train.py — Isolation Forest per vital sign + SHAP explainability
↓
dbt — staging → intermediate → mart layer transformations
↓
visualize.py — time-series plots with anomalies highlighted
↓
Airflow DAG — orchestrates all steps on a daily schedule
---

## Results

| Vital Sign | Total Readings | Anomalies Detected |
|---|---|---|
| Heart Rate | 13,913 | 696 (5.0%) |
| SpO2 | 13,540 | 677 (5.0%) |
| Systolic BP | 8,347 | 418 (5.0%) |
| Diastolic BP | 8,349 | 418 (5.0%) |
| **Total** | **44,149** | **2,209** |

Anomaly severity breakdown from the dbt mart layer:

| Severity | Count |
|---|---|
| Normal | 41,940 |
| Low | 1,190 |
| Medium | 700 |
| High | 319 |

Data validation identified 3 heart rate readings of 0 BPM — physiologically impossible in living patients — flagged and saved to a separate violations table before model training.

---

## Tech Stack

| Layer | Tool |
|---|---|
| Data source | MIMIC-IV Demo (PhysioNet) |
| Database | MySQL |
| Data processing | Python, Pandas, SQLAlchemy |
| Data validation | Custom physiologic threshold checks |
| Feature engineering | Rolling statistics, lag features, rate of change |
| Anomaly detection | Isolation Forest (scikit-learn) |
| Explainability | SHAP |
| Data transformation | dbt (staging → intermediate → marts) |
| Visualization | Matplotlib |
| Orchestration | Apache Airflow |

---

## Project Structure
patient-vitals-anomaly-detection/
├── src/
│   ├── ingest.py            # Chunk-based ingestion of MIMIC-IV vitals into MySQL
│   ├── validate.py          # Missingness and physiologic threshold validation
│   ├── features.py          # Rolling mean, std, lag, rate of change engineering
│   ├── train.py             # Isolation Forest training + SHAP explainability
│   └── visualize.py         # Time-series anomaly plots + SHAP summary chart
├── dbt_project/
│   └── models/
│       ├── staging/
│       │   └── stg_vitals.sql           # Standardize raw vitals
│       ├── intermediate/
│       │   └── int_vitals_features.sql  # SQL window function feature engineering
│       └── marts/
│           └── mart_anomaly_summary.sql # Final anomaly summary with severity labels
├── dags/
│   └── vitals_pipeline_dag.py  # Airflow DAG — daily orchestration
├── data/
│   ├── raw/                    # MIMIC-IV demo CSV files
│   ├── processed/              # Cleaned data
│   └── anomalies/              # Output charts (patient plots + SHAP summary)
└── notebooks/                  # Exploratory analysis
---

## Getting Started

### Prerequisites
- Python 3.11+
- MySQL 8.0
- Apache Airflow
- dbt-mysql

### Installation

```bash
git clone https://github.com/your-username/patient-vitals-anomaly-detection.git
cd patient-vitals-anomaly-detection
pip install pandas sqlalchemy pymysql scikit-learn shap matplotlib seaborn apache-airflow dbt-mysql
```

### Database Setup

Create the database in MySQL:

```sql
CREATE DATABASE patient_vitals;
```

### Data Access

This project uses the MIMIC-IV Demo dataset, freely available without credentialing at:
https://physionet.org/content/mimic-iv-demo/2.2/

Download and place these files in `data/raw/`:
- `patients.csv`
- `admissions.csv`
- `icustays.csv`
- `chartevents.csv`

### Running the Pipeline

Run each step manually:

```bash
python3 src/ingest.py
python3 src/validate.py
python3 src/features.py
python3 src/train.py
python3 src/visualize.py
```

Run dbt transformations:

```bash
cd dbt_project
dbt run
```

Or trigger the full pipeline via Airflow:

```bash
export AIRFLOW_HOME=~/path/to/project/airflow
airflow standalone
```

Then open http://localhost:8080 and trigger the `patient_vitals_anomaly_detection` DAG.

---

## Key Engineering Decisions

**Chunk-based ingestion:** `chartevents.csv` contains all ICU readings across all patients. Reading it in chunks of 100,000 rows prevents memory overflow on large datasets.

**Per-vital-sign modeling:** Training a separate Isolation Forest for each vital sign ensures anomaly scores are relative to that signal's own distribution — a heart rate of 140 is evaluated differently than a blood pressure of 140.

**SHAP explainability:** In healthcare contexts, knowing that a reading was flagged is not enough — clinicians need to know which feature drove the flag. SHAP provides feature-level attribution for every anomalous reading.

**dbt layering:** The three-layer dbt architecture (staging → intermediate → marts) mirrors production data warehouse patterns, making transformations testable, documented, and reusable.

---

## Sample Output

Patient time-series plots with anomalous readings highlighted in red are saved to `data/anomalies/`. A SHAP summary chart shows which features most commonly drove anomaly flags across all vital signs.

---

## References

- MIMIC-IV Demo: https://physionet.org/content/mimic-iv-demo/2.2/
- Isolation Forest: Liu et al., 2008
- SHAP: Lundberg & Lee, 2017
- dbt documentation: https://docs.getdbt.com
- Apache Airflow: https://airflow.apache.org