import pandas as pd
import json
from datetime import datetime

# --- Configuration ---
INPUT_CSV = "system_log.csv"
OUTPUT_JSON = "user_profile.json"

# Define your typical "work hours" to separate the data
WORK_START_HOUR = 9  # 9 AM
WORK_END_HOUR = 23 # 11 PM
WORK_DAYS = [0, 1, 2, 3, 4, 5, 6] # 0=Monday, ..., 6=Sunday

def analyze_performance_data():
    """
    Reads the system log, calculates performance and battery drain baselines,
    and saves them to a JSON profile file.
    """
    from database_manager import DatabaseManager
    
    print(f"Analyzing data from database...")
    try:
        db = DatabaseManager()
        # Fetch up to 10,000 recent records for analysis (enough for a week of minute-by-minute data)
        df = db.get_recent_history(limit=10000)
        
        if df.empty:
            print("No data found in database. Run the data logger first.")
            return

    except Exception as e:
        print(f"Error accessing database: {e}")
        return

    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # --- NEW: Calculate Your Personal Battery Drain Rate ---
    # 1. Filter the data to only include times when the laptop was unplugged.
    discharging_df = df[df['is_charging'] == False].copy()
    
    # 2. Calculate the change in battery level between each 1-minute reading.
    #    A positive number here means the battery level went down (a drain).
    discharging_df['drain_rate'] = -discharging_df['battery_percentage'].diff()
    
    # 3. Calculate the average drain rate (percentage points per minute).
    #    We use .dropna() to ignore the very first entry which has no previous point to compare to.
    avg_drain_rate = discharging_df['drain_rate'].dropna().mean()
    print(f"Calculated average battery drain rate: {avg_drain_rate:.2f}% per minute.")
    
    # --- The existing CPU/Memory analysis logic remains the same ---
    is_workday = df['timestamp'].dt.dayofweek.isin(WORK_DAYS)
    is_workhour = (df['timestamp'].dt.hour >= WORK_START_HOUR) & (df['timestamp'].dt.hour < WORK_END_HOUR)
    work_hours_data = df[is_workday & is_workhour]
    off_hours_data = df[~(is_workday & is_workhour)]

    print(f"Found {len(work_hours_data)} entries for 'work hours'.")
    print(f"Found {len(off_hours_data)} entries for 'off-hours'.")

    # --- Compile all the learned intelligence into a single profile ---
    profile = {
        "work_hours_cpu": {
            "avg": work_hours_data['cpu_load'].mean(),
            "std": work_hours_data['cpu_load'].std()
        },
        "off_hours_cpu": {
            "avg": off_hours_data['cpu_load'].mean(),
            "std": off_hours_data['cpu_load'].std()
        },
        # --- NEW: Add the calculated drain rate to the profile ---
        "avg_battery_drain_per_minute": avg_drain_rate,
        "profile_creation_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # --- Save the final profile to the JSON file ---
    with open(OUTPUT_JSON, 'w') as f:
        json.dump(profile, f, indent=4)
        
    print(f"\nSuccessfully updated personal performance profile at '{OUTPUT_JSON}'")

if __name__ == "__main__":
    analyze_performance_data()





