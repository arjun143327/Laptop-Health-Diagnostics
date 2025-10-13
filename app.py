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
from details_window import DetailsWindow

# --- (No changes to your constants) ---
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
        # --- (No changes to your existing __init__ method) ---
        self.root = root
        self.setup_window()
        self.system_monitor = SystemMonitor()
        self.health_calculator = HealthCalculator()
        self.graph_win = None
        self.details_win = None
        self.user_profile = self.load_user_profile()
        self.alert_cooldowns = {}
        self.update_job = None
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.create_gui()
        self.update_loop()

    def on_closing(self):
        if self.update_job: self.root.after_cancel(self.update_job)
        self.root.destroy()

    def load_user_profile(self):
        try:
            with open("user_profile.json", 'r') as f: return json.load(f)
        except FileNotFoundError: return None

    # --- (No changes to setup_window, create_gui, create_header_frame, create_score_frame, create_metrics_frame) ---
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
            if key in ["cpu", "memory"]:
                gauge.details_button.grid()
                gauge.details_button.configure(command=lambda k=key: self.show_details(k))
    
    # --- MODIFICATION: Add an "Export Report" button to the footer ---
    def create_footer_frame(self):
        footer_frame = ctk.CTkFrame(self.root, fg_color=FRAME_BG_COLOR, corner_radius=0)
        footer_frame.grid(row=2, column=0, sticky="ew")
        footer_frame.grid_columnconfigure(1, weight=1)
        
        self.status_label = ctk.CTkLabel(footer_frame, text="Last updated: --", font=("Segoe UI", 12), text_color="#AAB1C2")
        self.status_label.grid(row=0, column=0, padx=20, pady=8, sticky="w")

        # Create a frame to hold the buttons on the right
        button_frame = ctk.CTkFrame(footer_frame, fg_color="transparent")
        button_frame.grid(row=0, column=2, padx=20, pady=8, sticky="e")

        history_button = ctk.CTkButton(
            button_frame, text="📈 View History", font=("Segoe UI", 12),
            fg_color=ACCENT_COLOR, hover_color="#3B7BC2", command=self.open_graph_window
        )
        history_button.pack(side="right", padx=(10, 0))

        # --- NEW "Export Report" button ---
        export_button = ctk.CTkButton(
            button_frame, text="📋 Export Report", font=("Segoe UI", 12),
            fg_color="#3D4460", hover_color="#565F82", command=self.export_report
        )
        export_button.pack(side="right")

    # --- (No changes to open_graph_window or show_details) ---
    def open_graph_window(self):
        if self.graph_win is None or not self.graph_win.winfo_exists():
            self.graph_win = GraphWindow(self.root)
            self.graph_win.grab_set()
        else:
            self.graph_win.focus()

    def show_details(self, metric_type):
        if self.details_win is None or not self.details_win.winfo_exists():
            if metric_type == "cpu":
                title = "Top 5 Processes by CPU Usage"
                data = self.system_monitor.get_top_processes_by_cpu()
            elif metric_type == "memory":
                title = "Top 5 Processes by Memory Usage"
                data = self.system_monitor.get_top_processes_by_memory()
            else: return
            self.details_win = DetailsWindow(title, data)
            self.details_win.grab_set()
        else:
            self.details_win.focus()

    # --- NEW FUNCTION: The core logic for generating the report ---
    def export_report(self):
        """Gathers all current data and generates an HTML health report."""
        print("Generating health report...")
        
        # 1. Gather all necessary data
        metrics = self.system_monitor.get_all_metrics()
        health_score, status_info = self.health_calculator.calculate_health_score(metrics)
        system_info = self.system_monitor.get_system_info()
        cpu_avg = self.user_profile['work_hours_cpu']['avg'] if self.user_profile else 'N/A'
        
        # Helper to get metric values safely
        def get_metric_val(key):
            return metrics.get(key, {}).get('value', 0)

        # 2. Build the HTML content using an f-string
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>System Health Report</title>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background-color: #24293E; color: #E0E0E0; margin: 0; padding: 20px; }}
                .container {{ max-width: 800px; margin: auto; background-color: #2C324A; border-radius: 8px; padding: 30px; box-shadow: 0 4px 15px rgba(0,0,0,0.2); }}
                h1, h2 {{ color: #4A90E2; border-bottom: 2px solid #3D4460; padding-bottom: 10px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #3D4460; }}
                th {{ background-color: #3D4460; }}
                .score {{ font-size: 2.5em; font-weight: bold; color: {status_info['color']}; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>System Health Snapshot</h1>
                <p>Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                
                <h2>Overall Health Score</h2>
                <p class="score">{health_score:.1f} / 100 ({status_info['text']})</p>

                <h2>System Specifications</h2>
                <p><strong>Operating System:</strong> {system_info['os']}<br>
                   <strong>CPU Cores:</strong> {system_info['cpu']}</p>

                <h2>Live Metrics Breakdown</h2>
                <table>
                    <tr><th>Metric</th><th>Current Value</th><th>Personal Average (Work Hours)</th></tr>
                    <tr><td>CPU Load</td><td>{get_metric_val('cpu'):.1f}%</td><td>{cpu_avg:.1f}%</td></tr>
                    <tr><td>Memory Usage</td><td>{get_metric_val('memory'):.1f}%</td><td>N/A</td></tr>
                    <tr><td>Disk Usage</td><td>{get_metric_val('disk'):.1f}%</td><td>N/A</td></tr>
                    {"<tr><td>Battery</td><td>"+f"{get_metric_val('battery'):.0f}%"+"</td><td>N/A</td></tr>" if metrics.get('battery') else ""}
                </table>
            </div>
        </body>
        </html>
        """
        
        # 3. Save the HTML file
        filename = f"Health-Report-{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.html"
        try:
            with open(filename, "w", encoding='utf-8') as f:
                f.write(html_content)
            print(f"Report successfully saved as {filename}")
            AlertWindow("Report Generated", f"Snapshot saved successfully as:\n{filename}")
        except Exception as e:
            print(f"Error saving report: {e}")
            AlertWindow("Error", "Could not save the report.")

    # --- (No changes to update_loop, check_for_anomalies, trigger_alert) ---
    def update_loop(self):
        try:
            metrics = self.system_monitor.get_all_metrics()
            self.check_for_anomalies(metrics)
            for key, gauge in self.gauges.items():
                if metrics.get(key): gauge.update_value(metrics[key]['value'])
            health_score, status_info = self.health_calculator.calculate_health_score(metrics)
            self.health_score_gauge.update_value(health_score, status_info['text'], status_info['color'])
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.status_label.configure(text=f"Last updated: {current_time}")
        except Exception as e:
            print(f"Error in update loop: {e}")
        self.update_job = self.root.after(2000, self.update_loop)

    def check_for_anomalies(self, metrics):
        if not self.user_profile: return
        now = datetime.now()
        is_work_hours = (now.weekday() < 5 and 9 <= now.hour < 18)
        profile_key = 'work_hours_cpu' if is_work_hours else 'off_hours_cpu'
        cpu_profile = self.user_profile.get(profile_key, {})
        cpu_avg = cpu_profile.get('avg', 50)
        cpu_std = cpu_profile.get('std', 15)
        cpu_threshold = cpu_avg + (2 * cpu_std)
        current_cpu = metrics['cpu']['value']
        if current_cpu > cpu_threshold:
            self.trigger_alert("cpu", "High CPU Usage!", f"CPU load is at {current_cpu:.1f}%. Your average is {cpu_avg:.1f}%.")

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

