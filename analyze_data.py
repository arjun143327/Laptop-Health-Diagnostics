import pandas as pd
import json
from datetime import datetime

# --- Configuration ---
INPUT_CSV = "system_log.csv"
OUTPUT_JSON = "user_profile.json"

# Define your typical "work hours"
# You can adjust these to match your schedule
WORK_START_HOUR = 9  # 9 AM
WORK_END_HOUR = 23 # 6 PM
WORK_DAYS = [0, 1, 2, 3, 4, 5, 6] # 0=Monday, 1=Tuesday, ..., 4=Friday

def analyze_performance_data():
    """
    Reads the system log, calculates performance baselines for different
    time periods, and saves them to a JSON profile file.
    """
    print(f"Analyzing data from '{INPUT_CSV}'...")
    try:
        df = pd.read_csv(INPUT_CSV)
    except FileNotFoundError:
        print(f"Error: {INPUT_CSV} not found. Please run the logger first.")
        return

    df['timestamp'] = pd.to_datetime(df['timestamp'])

    is_workday = df['timestamp'].dt.dayofweek.isin(WORK_DAYS)
    is_workhour = (df['timestamp'].dt.hour >= WORK_START_HOUR) & (df['timestamp'].dt.hour < WORK_END_HOUR)

    work_hours_data = df[is_workday & is_workhour]
    off_hours_data = df[~(is_workday & is_workhour)]

    print(f"Found {len(work_hours_data)} entries for 'work hours'.")
    print(f"Found {len(off_hours_data)} entries for 'off-hours'.")

    profile = {
        "work_hours_cpu": {
            "avg": work_hours_data['cpu_load'].mean(),
            "std": work_hours_data['cpu_load'].std()
        },
        "work_hours_memory": {
            "avg": work_hours_data['memory_usage'].mean(),
            "std": work_hours_data['memory_usage'].std()
        },
        "off_hours_cpu": {
            "avg": off_hours_data['cpu_load'].mean(),
            "std": off_hours_data['cpu_load'].std()
        },
        "off_hours_memory": {
            "avg": off_hours_data['memory_usage'].mean(),
            "std": off_hours_data['memory_usage'].std()
        },
        "profile_creation_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    with open(OUTPUT_JSON, 'w') as f:
        json.dump(profile, f, indent=4)
        
    print(f"\nSuccessfully created personal performance profile at '{OUTPUT_JSON}'")

if __name__ == "__main__":
    analyze_performance_data()

