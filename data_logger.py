import psutil
import csv
from datetime import datetime
import time
import os

# --- Configuration ---
LOG_INTERVAL = 60  # seconds between each log entry
CSV_FILENAME = "system_log.csv"
CSV_HEADER = [
    "timestamp",
    "cpu_load",
    "memory_usage",
    "battery_percentage",
    "is_charging",
    "top_process_name",
    "top_process_cpu"
]


def get_top_process():
    """
    Iterates through all running processes to find the one using the most CPU.
    Returns the process name and its CPU usage.
    """
    try:
        # Get a list of all processes with their CPU usage and name
        processes = [p.info for p in psutil.process_iter(
            ['name', 'cpu_percent'])]

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
    is_charging = battery.power_plugged if battery else "N/A"

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
    Creates the CSV file with a header if it doesn't exist.
    """
    # Check if the CSV file needs a header
    file_exists = os.path.isfile(CSV_FILENAME)

    print("--- System Data Logger ---")
    print(f"Logging data every {LOG_INTERVAL} seconds to '{CSV_FILENAME}'")
    print("Press Ctrl+C to stop.")

    try:
        with open(CSV_FILENAME, mode='a', newline='', encoding='utf-8') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=CSV_HEADER)

            if not file_exists:
                writer.writeheader()  # Write header only once

            while True:
                # Get the latest metrics
                current_metrics = log_system_metrics()

                # Write the metrics to the CSV file
                writer.writerow(current_metrics)
                csv_file.flush()  # Ensure data is written immediately

                print(f"[{current_metrics['timestamp']}] Log entry saved. CPU: {current_metrics['cpu_load']}% | Top Process: {current_metrics['top_process_name']}")

                # Wait for the next interval
                time.sleep(LOG_INTERVAL)

    except KeyboardInterrupt:
        print("\nLogger stopped by user. Data saved.")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
