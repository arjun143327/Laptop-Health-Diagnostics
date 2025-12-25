import customtkinter as ctk
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates

# Set a professional, dark theme for the graph to match the app
plt.style.use("dark_background")

class GraphWindow(ctk.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("System Performance History")
        self.geometry("900x600")
        self.configure(fg_color="#2C324A")
        
        self.label = ctk.CTkLabel(self, text="Loading graph data...", font=("Segoe UI", 16))
        self.label.pack(pady=20)
        
        # Load and create graph in a separate step to allow the "Loading" message to show
        self.after(100, self.create_graph)

    def load_data(self):
        """Loads and prepares system log data for plotting."""
        from database_manager import DatabaseManager
        
        try:
            db = DatabaseManager()
            df = db.get_recent_history(limit=1000)
            
            if df.empty:
                self.label.configure(text="No data available.\nPlease ensure the data logger is running.")
                return None
                
            return df
        except Exception as e:
            self.label.configure(text=f"Error loading data: {e}")
            return None

    def create_graph(self):
        """Creates and embeds a readable, well-formatted Matplotlib graph."""
        data = self.load_data()
        
        if data is None or data.empty:
            return

        self.label.pack_forget() # Remove the "Loading" label once data is ready

        # Create the plot with improved aesthetics
        fig, ax1 = plt.subplots(figsize=(8, 5))
        fig.patch.set_facecolor("#2C324A") # Match the window background
        ax1.set_facecolor("#24293E") # Set the plot area background

        # Plot CPU Data (Blue)
        ax1.plot(data['timestamp'], data['cpu_load'], color='#4A90E2', label='CPU Load (%)', linewidth=1.5)
        
        # Create a second Y-axis for Memory that shares the same X-axis
        ax2 = ax1.twinx()
        
        # Plot Memory Data (Green)
        ax2.plot(data['timestamp'], data['memory_usage'], color='#2CC990', label='Memory Usage (%)', linewidth=1.5)

        # --- KEY FIXES FOR READABILITY ---
        # 1. Add a grid for easier reading
        ax1.grid(True, linestyle='--', alpha=0.3)
        
        # 2. Set clear labels for all axes
        ax1.set_xlabel("Time", fontsize=12, color="#AAB1C2")
        ax1.set_ylabel("CPU Load (%)", color='#4A90E2', fontsize=12)
        ax2.set_ylabel("Memory Usage (%)", color='#2CC990', fontsize=12)

        # 3. Color the axis numbers to match their corresponding lines
        ax1.tick_params(axis='y', labelcolor='#4A90E2')
        ax2.tick_params(axis='y', labelcolor='#2CC990')
        ax1.tick_params(axis='x', colors="#AAB1C2", labelrotation=25)
        
        # 4. Create a single, clear legend for both lines
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax2.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

        # 5. Format the timestamp on the X-axis to be clean and readable
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M\n%m-%d'))
        fig.tight_layout() # Adjust plot to prevent labels from overlapping

        # Embed the finished, readable plot into the CustomTkinter window
        canvas = FigureCanvasTkAgg(fig, self)
        canvas.draw()
        canvas.get_tk_widget().pack(side="top", fill="both", expand=True, padx=10, pady=10)

