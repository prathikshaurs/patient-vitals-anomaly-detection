#!/Users/prathikshamohanrajeurs/anaconda3/bin/python3

# To plot vital signs over time with anomalies highlighted

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from sqlalchemy import create_engine
import os

# DB connection
engine = create_engine('mysql+pymysql://root:root1234@127.0.0.1/patient_vitals')

# Output folder
OUTPUT_PATH = 'data/anomalies/'

def load_results():
    """Load anomaly results from MySQL"""
    print("Loading anomaly results from MySQL....")
    df = pd.read_sql('SELECT * FROM anomaly_results', engine)
    df['charttime'] = pd.to_datetime(df['charttime'])
    print(f"Loaded {len(df)} rows")
    return df

def get_sample_patients(df, n=3):
    """
    Pick n patients that have all 4 vital signs recorded
    and have at least some anomalies detected
    """
    # Find patients with anomalies
    patients_with_anomalies = df[df['anomaly_flag'] == 1]['subject_id'].unique()
    
    # Find patients with multiple vital signs
    vital_counts = df.groupby('subject_id')['vital_sign'].nunique()
    patients_with_all_vitals = vital_counts[vital_counts >= 3].index
    
    # Get patients that satisfy both conditions
    good_patients = list(set(patients_with_anomalies) & set(patients_with_all_vitals))
    
    return good_patients[:n]

def plot_patient_vitals(df, subject_id):
    """
    Plot all 4 vital signs for a single patient
    with anomalies highlighted in red
    """
    patient_df = df[df['subject_id'] == subject_id].copy()
    vitals = patient_df['vital_sign'].unique()
    
    fig, axes = plt.subplots(len(vitals), 1, figsize=(14, 4 * len(vitals)))
    fig.suptitle(f'Vital Signs - Patient {subject_id}', fontsize=14, fontweight='bold')
    
    if len(vitals) == 1:
        axes = [axes]
    
    for ax, vital in zip(axes, vitals):
        vital_df = patient_df[patient_df['vital_sign'] == vital].sort_values('charttime')
        
        # Normal readings
        normal = vital_df[vital_df['anomaly_flag'] == 0]
        anomalous = vital_df[vital_df['anomaly_flag'] == 1]
        
        # Plot normal readings as blue line
        ax.plot(normal['charttime'], normal['value'],
                color='steelblue', linewidth=1.5, label='Normal')
        
        # Plot anomalous readings as red dots
        ax.scatter(anomalous['charttime'], anomalous['value'],
                   color='red', s=60, zorder=5, label='Anomaly')
        
        # Formatting
        ax.set_title(vital.replace('_', ' ').title(), fontsize=11)
        ax.set_ylabel('Value')
        ax.legend(loc='upper right')
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Save chart
    output_file = f'{OUTPUT_PATH}patient_{subject_id}_vitals.png'
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved chart for patient {subject_id} to {output_file}")

def plot_shap_summary(df):
    """
    Plot average SHAP values to show which features
    contributed most to anomaly detection
    """
    print("\nGenerating SHAP summary plot....")
    
    shap_cols = ['shap_value', 'shap_rolling_mean_3', 
                 'shap_rolling_std_3', 'shap_lag_1', 
                 'shap_rate_of_change']
    
    # Get anomalous readings only
    anomalous = df[df['anomaly_flag'] == 1]
    
    # Calculate mean absolute SHAP values per feature
    mean_shap = anomalous[shap_cols].abs().mean()
    mean_shap.index = ['Value', 'Rolling Mean', 
                       'Rolling Std', 'Lag 1', 
                       'Rate of Change']
    mean_shap = mean_shap.sort_values(ascending=True)
    
    # Plot
    fig, ax = plt.subplots(figsize=(10, 5))
    mean_shap.plot(kind='barh', ax=ax, color='steelblue')
    ax.set_title('Average Feature Importance in Anomaly Detection (SHAP)', 
                 fontsize=12, fontweight='bold')
    ax.set_xlabel('Mean Absolute SHAP Value')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    output_file = f'{OUTPUT_PATH}shap_summary.png'
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved SHAP summary plot to {output_file}")

def main():
    print("Starting visualization....")
    
    # Load data
    df = load_results()
    
    # Get sample patients
    sample_patients = get_sample_patients(df, n=3)
    print(f"\nSelected patients for visualization: {sample_patients}")
    
    # Plot each patient
    for patient_id in sample_patients:
        plot_patient_vitals(df, patient_id)
    
    # Plot SHAP summary
    plot_shap_summary(df)
    
    print("\nVisualization complete!")
    print(f"Charts saved to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()