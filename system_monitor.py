import psutil
import platform

class SystemMonitor:
    # --- (No changes to the first part of your class) ---
    def __init__(self):
        self.battery_available = hasattr(psutil, 'sensors_battery') and psutil.sensors_battery() is not None
        self.temps_available = hasattr(psutil, 'sensors_temperatures') and psutil.sensors_temperatures()

    def get_system_info(self):
        uname = platform.uname()
        return {"os": f"{uname.system} {uname.release}", "cpu": psutil.cpu_count(logical=True), "machine": uname.machine}
    
    def has_battery(self):
        return self.battery_available
        
    def get_cpu_metrics(self):
        cpu_load = psutil.cpu_percent(interval=1)
        return {'value': cpu_load, 'display': f"{cpu_load:.1f}%"}

    def get_memory_metrics(self):
        mem = psutil.virtual_memory()
        return {'value': mem.percent, 'display': f"{mem.percent:.1f}%"}

    def get_disk_metrics(self):
        disk = psutil.disk_usage('/')
        return {'value': disk.percent, 'display': f"{disk.percent:.1f}%"}

    def get_battery_metrics(self):
        if not self.battery_available: return None
        battery = psutil.sensors_battery()
        return {'value': battery.percent, 'display': f"{battery.percent:.0f}%", 'charging': battery.power_plugged}

    def get_all_metrics(self):
        return {
            "cpu": self.get_cpu_metrics(), "memory": self.get_memory_metrics(),
            "disk": self.get_disk_metrics(), "battery": self.get_battery_metrics(),
        }

    # --- THIS IS THE UPDATED FUNCTION ---
    def get_top_processes_by_cpu(self, count=5):
        """
        Returns a list of the top 'count' REAL processes sorted by CPU usage,
        filtering out common system placeholders.
        """
        try:
            procs = [p for p in psutil.process_iter(['pid', 'name'])]
            psutil.cpu_percent(interval=None) 
            
            for p in procs:
                try:
                    p.info['cpu_percent'] = psutil.Process(p.info['pid']).cpu_percent(interval=0.1)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    p.info['cpu_percent'] = 0

            # --- THE FIX: Filter out the placeholder processes ---
            ignore_list = ["System Idle Process", "System"]
            filtered_procs = [p.info for p in procs if p.info['name'] not in ignore_list]
            # --- END OF FIX ---

            sorted_procs = sorted(filtered_procs, key=lambda p: p['cpu_percent'], reverse=True)
            
            return [(p['name'], p['cpu_percent']) for p in sorted_procs[:count] if p['cpu_percent'] > 0]
        except (psutil.AccessDenied, IndexError):
            return []

    # --- (No changes to get_top_processes_by_memory) ---
    def get_top_processes_by_memory(self, count=5):
        try:
            processes = [p.info for p in psutil.process_iter(['name', 'memory_percent'])]
            sorted_processes = sorted(processes, key=lambda p: p['memory_percent'], reverse=True)
            return [(p['name'], p['memory_percent']) for p in sorted_processes[:count]]
        except (psutil.NoSuchProcess, psutil.AccessDenied, IndexError):
            return []

