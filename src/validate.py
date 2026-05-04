#!/Users/prathikshamohanrajeurs/anaconda3/bin/python3

# To check data quality of vital signs before ML processing

import pandas as pd
from sqlalchemy import create_engine

# DB connection
engine = create_engine('mysql+pymysql://root:root1234@127.0.0.1/patient_vitals')

# Physiologic thresholds - acceptable ranges for each vital sign
# Anything outside these ranges is physiologically impossible
THRESHOLDS = {
    'heart_rate':    {'min': 20,   'max': 300},
    'spo2':          {'min': 0,   'max': 100},
    'systolic_bp':   {'min': 0,   'max': 300},
    'diastolic_bp':  {'min': 0,   'max': 200}
}

def load_vitals():
    """Load raw vitals from MySQL"""
    print("Loading vitals from MySQL....")
    df = pd.read_sql('SELECT * FROM vitals_raw', engine)
    print(f"Loaded {len(df)} rows")
    return df

def check_missing_values(df):
    """Check for missing values in each column"""
    print("\n-- Missingness Check --")
    missing = df.isnull().sum()
    missing_pct = (missing / len(df) * 100).round(2)
    
    report = pd.DataFrame({
        'missing_count': missing,
        'missing_pct': missing_pct
    })
    
    print(report)
    return report

def check_physiologic_thresholds(df):
    """Flag readings outside physiologically acceptable ranges"""
    print("\n-- Physiologic Threshold Check --")
    
    violations = []
    
    for vital, bounds in THRESHOLDS.items():
        vital_df = df[df['vital_sign'] == vital].copy()
        
        # Find readings outside acceptable range
        out_of_range = vital_df[
            (vital_df['value'] < bounds['min']) |
            (vital_df['value'] > bounds['max'])
        ]
        
        print(f"{vital}: {len(out_of_range)} violations out of {len(vital_df)} readings")
        
        if len(out_of_range) > 0:
            out_of_range = out_of_range.copy()
            out_of_range['violation_type'] = 'out_of_range'
            out_of_range['threshold_min'] = bounds['min']
            out_of_range['threshold_max'] = bounds['max']
            violations.append(out_of_range)
    
    if violations:
        violations_df = pd.concat(violations, ignore_index=True)
        violations_df.to_sql('validation_violations', engine, if_exists='replace', index=False)
        print(f"\nTotal violations saved to MySQL: {len(violations_df)}")
    else:
        print("\nNo violations found!")
    
    return violations

def check_vital_distribution(df):
    """Print basic statistics for each vital sign"""
    print("\n-- Vital Sign Distribution --")
    for vital in THRESHOLDS.keys():
        vital_df = df[df['vital_sign'] == vital]['value']
        print(f"\n{vital}:")
        print(f"  Count : {len(vital_df)}")
        print(f"  Mean  : {vital_df.mean():.2f}")
        print(f"  Min   : {vital_df.min():.2f}")
        print(f"  Max   : {vital_df.max():.2f}")
        print(f"  Std   : {vital_df.std():.2f}")

def main():
    print("Starting data validation...")
    
    # Load data
    df = load_vitals()
    
    # Run checks
    check_missing_values(df)
    check_physiologic_thresholds(df)
    check_vital_distribution(df)
    
    print("\nData validation complete!")

if __name__ == "__main__":
    main()