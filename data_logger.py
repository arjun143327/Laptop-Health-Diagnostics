import psutil
import time
from datetime import datetime
from database_manager import DatabaseManager

# --- Configuration ---
LOG_INTERVAL = 60  # seconds between each log entry
CSV_FILENAME = "system_log.csv" # Kept for migration purpose

def get_top_process():
    """
    Iterates through all running processes to find the one using the most CPU.
    Returns the process name and its CPU usage.
    """
    try:
        # Get a list of all processes with their CPU usage and name
        # Optimization: Use iterator properly to avoid overhead
        processes = [p.info for p in psutil.process_iter(['name', 'cpu_percent'])]
        
        if not processes:
            return "N/A", 0.0

        # Sort the list by CPU usage in descending order
        top_process = sorted(
            processes, key=lambda p: p['cpu_percent'], reverse=True)[0]

        # Return the name and CPU usage of the top process
        return top_process['name'], top_process['cpu_percent']
    except (psutil.NoSuchProcess, psutil.AccessDenied, IndexError):
        # Handle cases where process list is empty or inaccessible
        return "N/A", 0.0


def log_system_metrics():
    """
    Gathers all required system metrics and returns them as a dictionary.
    """
    # Get battery info, handling systems with no battery
    battery = psutil.sensors_battery()
    battery_percentage = battery.percent if battery else "N/A"
    is_charging = battery.power_plugged if battery else False

    # Get the top process
    top_proc_name, top_proc_cpu = get_top_process()

    # Package all data into a dictionary
    metrics = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "cpu_load": psutil.cpu_percent(interval=1),
        "memory_usage": psutil.virtual_memory().percent,
        "battery_percentage": battery_percentage,
        "is_charging": is_charging,
        "top_process_name": top_proc_name,
        "top_process_cpu": top_proc_cpu,
    }
    return metrics


def main():
    """
    Main loop to log data at a set interval.
    Uses DatabaseManager to store data.
    """
    print("--- System Data Logger (Database Edition) ---")
    
    # Initialize Database Manager
    db = DatabaseManager()
    
    # Attempt migration if legacy CSV exists
    migrated_count = db.migrate_from_csv(CSV_FILENAME)
    if migrated_count > 0:
        print(f"Successfully migrated {migrated_count} records from old CSV to Database.")

    print(f"Logging data every {LOG_INTERVAL} seconds to SQLite DB.")
    print("Press Ctrl+C to stop.")

    try:
        while True:
            # Get the latest metrics
            current_metrics = log_system_metrics()

            # Insert into DB
            db.insert_metric(current_metrics)

            print(f"[{current_metrics['timestamp']}] Log entry saved. CPU: {current_metrics['cpu_load']}% | Top Process: {current_metrics['top_process_name']}")

            # Wait for the next interval
            time.sleep(LOG_INTERVAL)

    except KeyboardInterrupt:
        print("\nLogger stopped by user. Data saved.")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
