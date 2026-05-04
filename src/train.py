#!/Users/prathikshamohanrajeurs/anaconda3/bin/python3

# To train Isolation Forest model and generate anomaly scores

import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import shap
import warnings
warnings.filterwarnings('ignore')

# DB connection
engine = create_engine('mysql+pymysql://root:root1234@127.0.0.1/patient_vitals')

# Features to use for anomaly detection
FEATURE_COLS = ['value', 'rolling_mean_3', 'rolling_std_3', 'lag_1', 'rate_of_change']

def load_features():
    """Load engineered features from MySQL"""
    print("Loading features from MySQL...")
    df = pd.read_sql('SELECT * FROM vitals_features', engine)
    print(f"Loaded {len(df)} rows")
    return df

def train_isolation_forest(df):
    """
    Train Isolation Forest model on engineered features.
    We train one model per vital sign so each vital sign
    is compared against its own normal range.
    """
    print("\nTraining Isolation Forest models....")
    
    all_results = []
    
    for vital in df['vital_sign'].unique():
        print(f"\nProcessing {vital}...")
        
        # Filter for this vital sign
        vital_df = df[df['vital_sign'] == vital].copy()
        
        # Extract features
        X = vital_df[FEATURE_COLS].fillna(0)
        
        # Scale features
        # Why: Isolation Forest works better when features are on similar scales
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Train Isolation Forest
        # contamination=0.05 means we expect ~5% of readings to be anomalous
        model = IsolationForest(
            n_estimators=100,
            contamination=0.05,
            random_state=42
        )
        model.fit(X_scaled)
        
        # Generate anomaly scores and predictions
        # -1 = anomaly, 1 = normal
        vital_df['anomaly_score'] = model.decision_function(X_scaled)
        vital_df['anomaly_flag'] = model.predict(X_scaled)
        
        # Convert to 0/1 instead of 1/-1
        # 1 = anomalous, 0 = normal
        vital_df['anomaly_flag'] = (vital_df['anomaly_flag'] == -1).astype(int)
        
        # SHAP values
        print(f"  Calculating SHAP values for {vital}....")
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X_scaled)
        
        # Add SHAP values as columns
        for i, col in enumerate(FEATURE_COLS):
            vital_df[f'shap_{col}'] = shap_values[:, i]
        
        all_results.append(vital_df)
        
        # Print summary
        n_anomalies = vital_df['anomaly_flag'].sum()
        print(f"  Total readings : {len(vital_df)}")
        print(f"  Anomalies found: {n_anomalies} ({n_anomalies/len(vital_df)*100:.1f}%)")
    
    return pd.concat(all_results, ignore_index=True)

def save_results(df):
    """Save anomaly results to MySQL"""
    print("\nSaving results to MySQL....")
    df.to_sql('anomaly_results', engine, if_exists='replace', index=False)
    print(f"Saved {len(df)} rows to anomaly_results table")

def main():
    print("Starting model training....")
    df = load_features()
    results = train_isolation_forest(df)
    save_results(results)
    print("\nModel training complete!")

if __name__ == "__main__":
    main()