import customtkinter as ctk
from datetime import datetime
import json
import time

# --- Import all your custom project modules ---
from system_monitor import SystemMonitor
from health_calculator import HealthCalculator
from gauge_widget import CircularProgressGauge, LinearGaugeWidget
from graph_window import GraphWindow
from alert_window import AlertWindow

# --- Constants for Theming and Layout ---
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
APP_BG_COLOR = "#24293E"
FRAME_BG_COLOR = "#2C324A"
TEXT_COLOR = "#FFFFFF"
ACCENT_COLOR = "#4A90E2"


class SystemHealthMonitorApp:
    def __init__(self, root):
        self.root = root
        self.setup_window()

        self.system_monitor = SystemMonitor()
        self.health_calculator = HealthCalculator()
        
        self.graph_win = None
        self.user_profile = self.load_user_profile()
        self.alert_cooldowns = {}
        
        # --- FIX: These lines now live INSIDE the __init__ method ---
        self.update_job = None  # Variable to store the update loop ID
        # Link the window's close button [X] to our custom closing function
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        # --- --------------------------------------------------- ---

        self.create_gui()
        self.update_loop()

    # --- NEW: This is the custom closing function ---
    def on_closing(self):
        """Handles the window closing event to ensure a clean shutdown."""
        print("Closing application cleanly...")
        # If an update loop is scheduled, cancel it before closing
        if self.update_job:
            self.root.after_cancel(self.update_job)
        self.root.destroy()
    # --- ---------------------------------------- ---

    def load_user_profile(self):
        """Loads the personalized performance profile from the JSON file."""
        try:
            with open("user_profile.json", 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return None

    def setup_window(self):
        self.root.title("System Health Monitor")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.minsize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.root.configure(fg_color=APP_BG_COLOR)
        ctk.set_appearance_mode("dark")

    def create_gui(self):
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        self.create_header_frame()
        main_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        main_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 10))
        main_frame.grid_columnconfigure((0, 1), weight=1)
        main_frame.grid_rowconfigure(0, weight=1)
        self.create_score_frame(main_frame)
        self.create_metrics_frame(main_frame)
        self.create_footer_frame()

    def create_header_frame(self):
        header_frame = ctk.CTkFrame(self.root, fg_color=FRAME_BG_COLOR, corner_radius=0)
        header_frame.grid(row=0, column=0, sticky="ew")
        system_info = self.system_monitor.get_system_info()
        info_text = f"OS: {system_info['os']}  |  CPU Cores: {system_info['cpu']}"
        header_label = ctk.CTkLabel(header_frame, text=info_text, font=("Segoe UI", 14), text_color=TEXT_COLOR)
        header_label.pack(pady=10)

    def create_score_frame(self, parent):
        score_frame = ctk.CTkFrame(parent, fg_color="transparent")
        score_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        score_frame.grid_rowconfigure(1, weight=1)
        score_frame.grid_columnconfigure(0, weight=1)
        title_label = ctk.CTkLabel(score_frame, text="System Health Score", font=("Segoe UI Bold", 20), text_color=TEXT_COLOR)
        title_label.grid(row=0, column=0, pady=(10, 20))
        self.health_score_gauge = CircularProgressGauge(score_frame, size=220)
        self.health_score_gauge.grid(row=1, column=0, sticky="n")

    def create_metrics_frame(self, parent):
        metrics_frame = ctk.CTkFrame(parent, fg_color="transparent")
        metrics_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        metrics_frame.grid_columnconfigure(0, weight=1)
        title_label = ctk.CTkLabel(metrics_frame, text="Metrics Breakdown", font=("Segoe UI Bold", 20), text_color=TEXT_COLOR)
        title_label.pack(anchor="w", pady=(10, 20), padx=10)
        self.gauges = {}
        gauge_configs = [("cpu", "CPU Load", "💻"), ("memory", "Memory Usage", "🧠"), ("disk", "Disk Usage", "💾")]
        if self.system_monitor.has_battery():
            gauge_configs.append(("battery", "Battery", "🔋"))
        for key, name, icon in gauge_configs:
            gauge = LinearGaugeWidget(metrics_frame, name, icon)
            gauge.pack(fill="x", expand=True, pady=10, padx=10)
            self.gauges[key] = gauge

    def create_footer_frame(self):
        footer_frame = ctk.CTkFrame(self.root, fg_color=FRAME_BG_COLOR, corner_radius=0)
        footer_frame.grid(row=2, column=0, sticky="ew")
        footer_frame.grid_columnconfigure(1, weight=1)
        self.status_label = ctk.CTkLabel(footer_frame, text="Last updated: --", font=("Segoe UI", 12), text_color="#AAB1C2")
        self.status_label.grid(row=0, column=0, padx=20, pady=8, sticky="w")
        history_button = ctk.CTkButton(
            footer_frame, text="📈 View History", font=("Segoe UI", 12),
            fg_color=ACCENT_COLOR, hover_color="#3B7BC2", command=self.open_graph_window
        )
        history_button.grid(row=0, column=2, padx=20, pady=8, sticky="e")

    def open_graph_window(self):
        if self.graph_win is None or not self.graph_win.winfo_exists():
            self.graph_win = GraphWindow(self.root)
            self.graph_win.grab_set()
        else:
            self.graph_win.focus()

    def update_loop(self):
        try:
            metrics = self.system_monitor.get_all_metrics()
            self.check_for_anomalies(metrics)
            for key, gauge in self.gauges.items():
                if metrics.get(key):
                    gauge.update_value(metrics[key]['value'])
            health_score, status_info = self.health_calculator.calculate_health_score(metrics)
            self.health_score_gauge.update_value(health_score, status_info['text'], status_info['color'])
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.status_label.configure(text=f"Last updated: {current_time}")
        except Exception as e:
            print(f"Error in update loop: {e}")
        
        # --- FIX: Store the scheduled job ID ---
        self.update_job = self.root.after(2000, self.update_loop)

    def check_for_anomalies(self, metrics):
        if not self.user_profile:
            return

        now = datetime.now()
        is_work_hours = (now.weekday() < 5 and 9 <= now.hour < 18)
        profile_key = 'work_hours_cpu' if is_work_hours else 'off_hours_cpu'
        cpu_profile = self.user_profile.get(profile_key, {})
        
        cpu_avg = cpu_profile.get('avg', 50)
        cpu_std = cpu_profile.get('std', 15)
        cpu_threshold = cpu_avg + (2 * cpu_std)
        current_cpu = metrics['cpu']['value']

        if current_cpu > cpu_threshold:
            self.trigger_alert(
                "cpu", 
                "High CPU Usage Detected!", 
                f"Your CPU load is at {current_cpu:.1f}%, which is unusually high for your normal usage patterns at this time."
            )

    def trigger_alert(self, metric_key, title, message):
        current_time = time.time()
        cooldown_period = 300
        last_alert_time = self.alert_cooldowns.get(metric_key, 0)
        if (current_time - last_alert_time) > cooldown_period:
            AlertWindow(title, message)
            self.alert_cooldowns[metric_key] = current_time


if __name__ == "__main__":
    root = ctk.CTk()
    app = SystemHealthMonitorApp(root)
    root.mainloop()

