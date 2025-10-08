import psutil
import platform


class SystemMonitor:
    """
    A class to fetch various system metrics using the psutil library.
    Handles cases where certain metrics (like battery or temperature) may not be available.
    """

    def __init__(self):
        """Initializes the monitor and checks for available hardware sensors on startup."""
        self.battery_available = hasattr(
            psutil, 'sensors_battery') and psutil.sensors_battery() is not None
        self.temps_available = hasattr(
            psutil, 'sensors_temperatures') and psutil.sensors_temperatures()

    def get_system_info(self):
        """Returns basic static system information."""
        uname = platform.uname()
        return {
            "os": f"{uname.system} {uname.release}",
            "cpu": psutil.cpu_count(logical=True),
            "machine": uname.machine
        }

    def has_battery(self):
        """Checks if a battery is present on the system."""
        return self.battery_available

    def has_temps(self):
        """Checks if CPU temperatures can be read."""
        return self.temps_available

    def get_cpu_metrics(self):
        """Returns current CPU load percentage."""
        # This call is done once and the result is reused to avoid the 0% bug.
        cpu_load = psutil.cpu_percent(interval=1)
        return {'value': cpu_load, 'display': f"{cpu_load:.1f}%"}

    def get_memory_metrics(self):
        """Returns current memory usage percentage."""
        mem = psutil.virtual_memory()
        return {'value': mem.percent, 'display': f"{mem.percent:.1f}%"}

    def get_disk_metrics(self):
        """Returns disk usage percentage for the root partition."""
        disk = psutil.disk_usage('/')
        return {'value': disk.percent, 'display': f"{disk.percent:.1f}%"}

    def get_battery_metrics(self):
        """Returns battery percentage. Returns None if no battery is found."""
        if not self.battery_available:
            return None
        battery = psutil.sensors_battery()
        return {'value': battery.percent, 'display': f"{battery.percent:.0f}%"}

    def get_temperature_metrics(self):
        """
        Returns the average core CPU temperature. Returns None if temperatures cannot be read.
        This often requires administrator privileges and supported hardware.
        """
        if not self.temps_available:
            return None

        try:
            temps = psutil.sensors_temperatures()
            # Common sensor key for Intel/AMD CPUs
            if 'coretemp' in temps:
                core_temps = [temp.current for temp in temps['coretemp']]
                avg_temp = sum(core_temps) / \
                    len(core_temps) if core_temps else 0
                return {'value': avg_temp, 'display': f"{avg_temp:.1f}°C"}

            # Fallback for other possible sensor keys
            for key in temps:
                if temps[key]:
                    temp_val = temps[key][0].current
                    return {'value': temp_val, 'display': f"{temp_val:.1f}°C"}
        except Exception:
            # If any error occurs (e.g., permission denied), return None
            return None

        return None

    def get_all_metrics(self):
        """Returns a dictionary of all system metrics."""
        return {
            "cpu": self.get_cpu_metrics(),
            "memory": self.get_memory_metrics(),
            "disk": self.get_disk_metrics(),
            "battery": self.get_battery_metrics(),
            "temperature": self.get_temperature_metrics(),
        }
