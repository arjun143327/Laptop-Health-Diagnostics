import customtkinter as ctk
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# --- Constants for Theming ---
APP_BG_COLOR = "#24293E"
FRAME_BG_COLOR = "#2C324A"
TEXT_COLOR = "#FFFFFF"


class GraphWindow(ctk.CTkToplevel):
    """
    A pop-up window that displays a historical performance graph.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("Performance History")
        self.geometry("800x600")
        self.configure(fg_color=APP_BG_COLOR)

        self.minsize(600, 400)

        self.label = ctk.CTkLabel(
            self, text="Loading graph data...", font=("Segoe UI", 16))
        self.label.pack(pady=20, padx=20)

        # This function is called immediately to create the graph
        self.create_graph()

    def load_data(self):
        """Loads system log data from the CSV file using pandas."""
        try:
            df = pd.read_csv("system_log.csv", parse_dates=['timestamp'])
            # Use only the last 1000 data points to keep the graph from getting crowded
            return df.tail(1000)
        except FileNotFoundError:
            # Display a helpful message if the log file hasn't been created yet
            self.label.configure(
                text="Error: system_log.csv not found.\nPlease run data_logger.py to collect some data first.")
            return None

    def create_graph(self):
        """Creates and embeds a matplotlib graph into the CustomTkinter window."""
        data = self.load_data()

        if data is None or data.empty:
            return  # Stop if there is no data to plot

        self.label.pack_forget()  # Remove the "Loading..." label

        # --- Matplotlib Graph Creation ---
        plt.style.use('seaborn-v0_8-darkgrid')

        fig, ax1 = plt.subplots(figsize=(8, 5))
        fig.patch.set_facecolor(APP_BG_COLOR)

        # Plot CPU Load
        ax1.plot(data['timestamp'], data['cpu_load'],
                 color='#4A90E2', label='CPU Load (%)', linewidth=2)
        ax1.set_xlabel('Time', color=TEXT_COLOR, fontsize=12)
        ax1.set_ylabel('CPU Load (%)', color='#4A90E2', fontsize=12)
        ax1.tick_params(axis='y', labelcolor='#4A90E2')
        ax1.tick_params(axis='x', colors=TEXT_COLOR, rotation=30)

        # Create a second y-axis for Memory Usage
        ax2 = ax1.twinx()
        ax2.plot(data['timestamp'], data['memory_usage'],
                 color='#2CC990', label='Memory Usage (%)', linewidth=2)
        ax2.set_ylabel('Memory Usage (%)', color='#2CC900', fontsize=12)
        ax2.tick_params(axis='y', labelcolor='#2CC990')

        plt.title('System Performance History', color=TEXT_COLOR, fontsize=16)
        fig.tight_layout()  # Adjust plot to prevent labels from overlapping
        ax1.grid(True, which='both', linestyle='--',
                 linewidth=0.5, color=FRAME_BG_COLOR)
        ax2.grid(False)  # Only show the grid for the primary axis

        # --- Embed the Matplotlib graph into the CustomTkinter window ---
        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.draw()
        canvas.get_tk_widget().pack(side="top", fill="both", expand=True, padx=10, pady=10)
