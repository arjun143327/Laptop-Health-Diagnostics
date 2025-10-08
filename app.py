import customtkinter as ctk
import threading
import time
from datetime import datetime
from system_monitor import SystemMonitor
from gauge_widget import GaugeWidget
from health_calculator import HealthCalculator


class SystemHealthMonitorApp:
    """
    A GUI application to monitor system health metrics and display an overall health score.
    """

    def __init__(self, root):
        """
        Initializes the main application.
        """
        self.root = root
        self.root.title("System Health Monitor")
        self.root.geometry("1100x750")
        self.root.minsize(900, 600)

        # Set CustomTkinter appearance
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        # Initialize backend components
        self.system_monitor = SystemMonitor()
        self.health_calculator = HealthCalculator()

        # Control variable for the blinking effect
        self.blink_state = False

        # Variable to hold the current score
        self.current_score = 0

        # Build the GUI
        self.create_gui()

        # Start the first data update
        self.monitor_loop()
        # Start the blinking loop for the critical health score indicator
        self.blink_loop()

    def create_gui(self):
        """Creates the main GUI layout."""
        self.main_frame = ctk.CTkFrame(self.root, fg_color="#f8f9fa")
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.main_frame.grid_rowconfigure(2, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        self.create_system_info_panel()
        self.create_health_score_panel()
        self.create_gauges_panel()
        self.create_status_bar()

    def create_system_info_panel(self):
        """Creates the system information panel at the top."""
        info_frame = ctk.CTkFrame(
            self.main_frame, fg_color="#ffffff", corner_radius=10)
        info_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))

        system_info = self.system_monitor.get_system_info()
        info_text = f"🖥️ OS: {system_info['os']} | 💻 CPU Cores: {system_info['cpu']}"
        self.system_info_label = ctk.CTkLabel(
            info_frame,
            text=info_text,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#2c3e50"
        )
        self.system_info_label.pack(pady=10, padx=10)

    def create_health_score_panel(self):
        """Creates the main health score display panel."""
        health_frame = ctk.CTkFrame(
            self.main_frame, fg_color="#f0f8ff", corner_radius=15)
        health_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)

        title_label = ctk.CTkLabel(
            health_frame,
            text="SYSTEM HEALTH SCORE",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#2c3e50"
        )
        title_label.pack(pady=(15, 5))

        score_container = ctk.CTkFrame(
            health_frame, fg_color="#ffffff", corner_radius=15)
        score_container.pack(pady=10, padx=20, fill="x")

        self.health_score_label = ctk.CTkLabel(
            score_container,
            text="--",
            font=ctk.CTkFont(size=72, weight="bold"),
            text_color="#27ae60"
        )
        self.health_score_label.pack(pady=(20, 5))

        self.health_status_label = ctk.CTkLabel(
            score_container,
            text="Analyzing...",
            font=ctk.CTkFont(size=18),
            text_color="#7f8c8d"
        )
        self.health_status_label.pack(pady=(0, 20))

    def create_gauges_panel(self):
        """Creates the panel containing all the metric gauges."""
        gauges_title = ctk.CTkLabel(
            self.main_frame,
            text="📊 METRICS BREAKDOWN",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#2c3e50"
        )
        gauges_title.grid(row=2, column=0, sticky="sw", padx=15, pady=(10, 5))

        gauges_frame = ctk.CTkFrame(
            self.main_frame, fg_color="#ffffff", corner_radius=10)
        gauges_frame.grid(row=3, column=0, sticky="nsew",
                          padx=10, pady=(0, 10))
        gauges_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.gauges = {}
        gauge_configs = [
            ("CPU Load", "cpu", "#FF6B6B"),
            ("Memory Usage", "memory", "#4ECDC4"),
            ("Disk Usage", "disk", "#45B7D1"),
            ("Battery", "battery", "#96CEB4"),
            ("CPU Temp", "temperature", "#FFA07A"),
        ]

        for i, (name, key, color) in enumerate(gauge_configs):
            row, col = divmod(i, 3)
            gauge = GaugeWidget(gauges_frame, name, color)
            gauge.grid(row=row, column=col, padx=10, pady=15, sticky="nsew")
            self.gauges[key] = gauge

        # Handle case where battery is not available
        if not self.system_monitor.has_battery():
            self.gauges['battery'].update_value(None, "N/A")

    def create_status_bar(self):
        """Creates the status bar at the bottom."""
        status_frame = ctk.CTkFrame(
            self.main_frame, fg_color="#ecf0f1", corner_radius=5, height=30)
        status_frame.grid(row=4, column=0, sticky="ew", padx=10, pady=(5, 10))

        self.status_label = ctk.CTkLabel(
            status_frame,
            text="Last updated: --",
            font=ctk.CTkFont(size=12),
            text_color="#7f8c8d"
        )
        self.status_label.pack(pady=5, padx=10, side="left")

    def monitor_loop(self):
        """
        Main monitoring loop. Fetches data and updates the GUI.
        Uses root.after() to run safely in the main GUI thread.
        """
        try:
            metrics = self.system_monitor.get_all_metrics()
            self.update_gauges(metrics)

            health_score, score_status = self.health_calculator.calculate_health_score(
                metrics)
            self.update_health_score(health_score, score_status)

            self.update_status()
        except Exception as e:
            print(f"Error in monitoring loop: {e}")
        finally:
            # Schedule the next update
            self.root.after(2000, self.monitor_loop)

    def update_gauges(self, metrics):
        """Updates all gauge widgets with current metric values."""
        for key, gauge in self.gauges.items():
            if key in metrics and metrics[key] is not None:
                gauge.update_value(
                    metrics[key]['value'], metrics[key]['display'])
            elif key == 'battery' and not self.system_monitor.has_battery():
                gauge.update_value(0, "N/A")

    def update_health_score(self, score, status):
        """Updates the health score display with appropriate color and status text."""
        self.current_score = score
        color = status['color']

        self.health_score_label.configure(text=f"{score:.0f}")
        self.health_status_label.configure(
            text=f"{status['emoji']} {status['text']}", text_color=color)

        # Apply blinking effect for critical scores
        if status['text'] == "CRITICAL":
            if self.blink_state:
                self.health_score_label.configure(text_color=color)
            else:
                self.health_score_label.configure(
                    text_color="#c0392b")  # Darker red
        else:
            self.health_score_label.configure(text_color=color)

    def update_status(self):
        """Updates the status bar with the current timestamp."""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.status_label.configure(text=f"Last updated: {current_time}")

    def blink_loop(self):
        """
        Controls the blinking state for critical warnings.
        Runs safely in the main thread using `root.after`.
        """
        self.blink_state = not self.blink_state

        # Get the latest status based on the current score and re-apply it
        score_status = self.health_calculator.get_score_status(
            self.current_score)
        self.update_health_score(self.current_score, score_status)

        self.root.after(500, self.blink_loop)


if __name__ == "__main__":
    root = ctk.CTk()
    app = SystemHealthMonitorApp(root)
    root.mainloop()
