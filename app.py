import customtkinter as ctk
from system_monitor import SystemMonitor
from gauge_widget import CircularProgressGauge, LinearGaugeWidget
from health_calculator import HealthCalculator
from datetime import datetime

# --- Constants for Theming and Layout ---
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
APP_BG_COLOR = "#24293E"
FRAME_BG_COLOR = "#2C324A"
TEXT_COLOR = "#FFFFFF"
ACCENT_COLOR = "#4A90E2"
GREEN = "#2CC990"
ORANGE = "#F7A02B"
RED = "#E94B3C"


class SystemHealthMonitorApp:
    def __init__(self, root):
        self.root = root
        self.setup_window()

        self.system_monitor = SystemMonitor()
        self.health_calculator = HealthCalculator()

        self.create_gui()
        self.update_loop()

    def setup_window(self):
        """Configure the main application window."""
        self.root.title("System Health Monitor")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.minsize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.root.configure(fg_color=APP_BG_COLOR)
        ctk.set_appearance_mode("dark")

    def create_gui(self):
        """Create the main graphical user interface."""
        # --- Main Grid Layout ---
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)

        # --- Header Frame ---
        self.create_header_frame()

        # --- Main Content Frame ---
        main_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        main_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 10))
        main_frame.grid_columnconfigure((0, 1), weight=1)
        main_frame.grid_rowconfigure(0, weight=1)

        # --- Health Score Frame (Left) ---
        self.create_score_frame(main_frame)

        # --- Metrics Breakdown Frame (Right) ---
        self.create_metrics_frame(main_frame)

        # --- Footer Frame ---
        self.create_footer_frame()

    def create_header_frame(self):
        """Create the top header with system info."""
        header_frame = ctk.CTkFrame(
            self.root, fg_color=FRAME_BG_COLOR, corner_radius=0)
        header_frame.grid(row=0, column=0, sticky="ew")

        system_info = self.system_monitor.get_system_info()
        info_text = f"OS: {system_info['os']}  |  CPU Cores: {system_info['cpu']}"

        header_label = ctk.CTkLabel(header_frame, text=info_text, font=(
            "Segoe UI", 14), text_color=TEXT_COLOR)
        header_label.pack(pady=10)

    def create_score_frame(self, parent):
        """Create the main health score circular gauge."""
        score_frame = ctk.CTkFrame(parent, fg_color="transparent")
        score_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        score_frame.grid_rowconfigure(1, weight=1)
        score_frame.grid_columnconfigure(0, weight=1)

        title_label = ctk.CTkLabel(score_frame, text="System Health Score", font=(
            "Segoe UI Bold", 20), text_color=TEXT_COLOR)
        title_label.grid(row=0, column=0, pady=(10, 20))

        self.health_score_gauge = CircularProgressGauge(score_frame, size=220)
        self.health_score_gauge.grid(row=1, column=0, sticky="n")

    def create_metrics_frame(self, parent):
        """Create the linear gauges for individual system metrics."""
        metrics_frame = ctk.CTkFrame(parent, fg_color="transparent")
        metrics_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        metrics_frame.grid_columnconfigure(0, weight=1)

        title_label = ctk.CTkLabel(metrics_frame, text="Metrics Breakdown", font=(
            "Segoe UI Bold", 20), text_color=TEXT_COLOR)
        title_label.pack(anchor="w", pady=(10, 20), padx=10)

        self.gauges = {}
        gauge_configs = [
            ("cpu", "CPU Load", "💻"),
            ("memory", "Memory Usage", "🧠"),
            ("disk", "Disk Usage", "💾"),
        ]

        # Conditionally add battery and temperature gauges
        if self.system_monitor.has_battery():
            gauge_configs.append(("battery", "Battery", "🔋"))
        if self.system_monitor.has_temps():
            gauge_configs.append(("temperature", "CPU Temp", "🌡️"))

        for key, name, icon in gauge_configs:
            gauge = LinearGaugeWidget(metrics_frame, name, icon)
            gauge.pack(fill="x", expand=True, pady=10, padx=10)
            self.gauges[key] = gauge

    def create_footer_frame(self):
        """Create the bottom footer with the last updated timestamp."""
        footer_frame = ctk.CTkFrame(
            self.root, fg_color=FRAME_BG_COLOR, corner_radius=0)
        footer_frame.grid(row=2, column=0, sticky="ew")

        self.status_label = ctk.CTkLabel(
            footer_frame, text="Last updated: --", font=("Segoe UI", 12), text_color="#AAB1C2")
        self.status_label.pack(pady=8)

    def update_loop(self):
        """The main loop to update all GUI elements."""
        try:
            metrics = self.system_monitor.get_all_metrics()

            # Update individual metric gauges
            for key, gauge in self.gauges.items():
                if metrics.get(key):
                    gauge.update_value(metrics[key]['value'])

            # Calculate and update the main health score
            health_score, status_info = self.health_calculator.calculate_health_score(
                metrics)
            self.health_score_gauge.update_value(
                health_score, status_info['text'], status_info['color'])

            # Update footer timestamp
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.status_label.configure(text=f"Last updated: {current_time}")

        except Exception as e:
            print(f"Error in update loop: {e}")

        self.root.after(2000, self.update_loop)


if __name__ == "__main__":
    root = ctk.CTk()
    app = SystemHealthMonitorApp(root)
    root.mainloop()
