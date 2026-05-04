#!/Users/prathikshamohanrajeurs/anaconda3/bin/python3

# To engineer features from raw vitals for anomaly detection

import pandas as pd
from sqlalchemy import create_engine

# DB connection
engine = create_engine('mysql+pymysql://root:root1234@127.0.0.1/patient_vitals')

def load_vitals():
    """Load raw vitals from MySQL"""
    print("Loading vitals from MySQL....")
    df = pd.read_sql('SELECT * FROM vitals_raw', engine)
    df['charttime'] = pd.to_datetime(df['charttime'])
    print(f"Loaded {len(df)} rows")
    return df

def engineer_features(df):
    """
    Create new features for each vital sign per patient per ICU stay.
    We group by patient + ICU stay + vital sign so features are
    calculated within each patient's own readings — not across patients.
    """
    print("Engineering features....")

    # Sort by patient, stay, vital sign and time
    df = df.sort_values(['subject_id', 'stay_id', 'vital_sign', 'charttime'])

    # Group by patient + stay + vital sign
    group_cols = ['subject_id', 'stay_id', 'vital_sign']

    # Rolling mean (last 3 readings)
    # Shows the recent average trend for this patient
    df['rolling_mean_3'] = df.groupby(group_cols)['value'].transform(
        lambda x: x.rolling(window=3, min_periods=1).mean()
    )

    # Rolling standard deviation (last 3 readings)
    # Shows how much the readings are varying recently
    df['rolling_std_3'] = df.groupby(group_cols)['value'].transform(
        lambda x: x.rolling(window=3, min_periods=1).std()
    )

    # Lag feature (previous reading)
    # The value from the immediately preceding reading
    df['lag_1'] = df.groupby(group_cols)['value'].transform(
        lambda x: x.shift(1)
    )

    # Rate of change (current minus previous reading)
    # How much the vital sign changed since last reading
    df['rate_of_change'] = df['value'] - df['lag_1']

    # Fill NaN values created by rolling/lag operations
    df['rolling_std_3'] = df['rolling_std_3'].fillna(0)
    df['lag_1'] = df['lag_1'].fillna(df['value'])
    df['rate_of_change'] = df['rate_of_change'].fillna(0)

    print("Features created:")
    print("  - rolling_mean_3  : average of last 3 readings")
    print("  - rolling_std_3   : std deviation of last 3 readings")
    print("  - lag_1           : previous reading value")
    print("  - rate_of_change  : change since last reading")

    return df

def save_features(df):
    """Save engineered features to MySQL"""
    print("\nSaving features to MySQL....")
    df.to_sql('vitals_features', engine, if_exists='replace', index=False)
    print(f"Saved {len(df)} rows to vitals_features table")

def main():
    print("Starting feature engineering....")
    df = load_vitals()
    df = engineer_features(df)
    save_features(df)
    print("\nFeature engineering complete!")

if __name__ == "__main__":
    main()