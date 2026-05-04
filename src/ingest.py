#!/Users/prathikshamohanrajeurs/anaconda3/bin/python3

# To read MIMIC-IV demo csv files and load them into MySQL DB

import pandas as pd
from sqlalchemy import create_engine

# DB connection
engine = create_engine('mysql+pymysql://root:root1234@127.0.0.1/patient_vitals')

RAW_DATA_PATH = '/Users/prathikshamohanrajeurs/Documents/patient-vitals-anomaly-detection/data/raw/'

# MIMIC item IDs for the vital signs that we need
VITAL_ITEM_IDS = {
    220045: 'heart_rate',
    220277: 'spo2',
    220179: 'systolic_bp',
    220180: 'diastolic_bp'
}

def load_patients():
    """load patients table to mysql"""
    print("Loading patients....")
    df = pd.read_csv(f'{RAW_DATA_PATH}patients.csv')
    df.to_sql('patients', engine, if_exists='replace', index=False)
    print(f"Loaded {len(df)} patients")

def load_admissions():
    """load admissions table to mysql"""
    print("Loading admissions....")
    df = pd.read_csv(f'{RAW_DATA_PATH}admissions.csv')
    df.to_sql('admissions', engine, if_exists='replace', index=False)
    print(f"Loaded {len(df)} admissions")

def load_icustays():
    """load ICU stays table to mysql"""
    print("Loading ICU stays....")
    df = pd.read_csv(f'{RAW_DATA_PATH}icustays.csv')
    df.to_sql('icustays', engine, if_exists='replace', index=False)
    print(f"Loaded {len(df)} ICU stays")

def load_vitals():
    """
    Load chartevents and filter only vital signs we need
    chartevents contains ALL ICU readings — we filter down
    to just HR, SpO2, and BP
    """
    print("Loading vital signs from chartevents....")
    
    chunks = []
    for chunk in pd.read_csv(f'{RAW_DATA_PATH}chartevents.csv', chunksize=100000):
        filtered = chunk[chunk['itemid'].isin(VITAL_ITEM_IDS.keys())]
        chunks.append(filtered)
    
    df = pd.concat(chunks, ignore_index=True)
    
    # Map item IDs to readable vital sign names
    df['vital_sign'] = df['itemid'].map(VITAL_ITEM_IDS)
    
    # Keep only columns we need
    df = df[['subject_id', 'hadm_id', 'stay_id', 'charttime', 'itemid', 'vital_sign', 'valuenum']]
    
    # Rename for clarity
    df.rename(columns={'valuenum': 'value'}, inplace=True)
    
    # Load into MySQL
    df.to_sql('vitals_raw', engine, if_exists='replace', index=False)
    print(f"Loaded {len(df)} vital sign readings")

def main():
    print("Starting data ingestion....")
    load_patients()
    load_admissions()
    load_icustays()
    load_vitals()
    print("All data successfully loaded into MySQL!")

if __name__ == "__main__":
    main()