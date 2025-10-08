import customtkinter as ctk
import math

# --- Constants for Theming ---
APP_BG_COLOR = "#24293E"
FRAME_BG_COLOR = "#2C324A"
TEXT_COLOR = "#FFFFFF"
ACCENT_COLOR = "#4A90E2"
GREEN = "#2CC990"
ORANGE = "#F7A02B"
RED = "#E94B3C"


class CircularProgressGauge(ctk.CTkFrame):
    """A circular gauge for displaying the main health score."""

    def __init__(self, master, size=200, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.size = size
        self.configure(width=size, height=size)

        self.canvas = ctk.CTkCanvas(
            self, width=size, height=size, bg=APP_BG_COLOR, highlightthickness=0)
        self.canvas.pack()

        self.value = 0
        self.text = "Loading..."
        self.color = "#FFFFFF"
        self.draw()

    def draw(self):
        """Draws all elements on the canvas."""
        self.canvas.delete("all")
        w, h = self.size, self.size

        # Draw the background track
        self.canvas.create_arc(
            w*0.1, h*0.1, w*0.9, h*0.9,
            start=90, extent=359.9, style="arc",
            outline=FRAME_BG_COLOR, width=w*0.08
        )

        # Draw the progress arc
        if self.value > 0:
            self.canvas.create_arc(
                w*0.1, h*0.1, w*0.9, h*0.9,
                start=90, extent=-(self.value / 100) * 360, style="arc",
                outline=self.color, width=w*0.08
            )

        # Draw the main score text
        self.canvas.create_text(
            w/2, h/2 - 15, text=f"{self.value:.0f}",
            font=("Segoe UI Bold", 60), fill=self.color
        )

        # Draw the status text
        self.canvas.create_text(
            w/2, h/2 + 35, text=self.text.upper(),
            font=("Segoe UI Bold", 16), fill=self.color
        )

    def update_value(self, value, text, color):
        """Updates the gauge's value, text, and color, and redraws it."""
        self.value = value
        self.text = text
        self.color = color
        self.draw()


class LinearGaugeWidget(ctk.CTkFrame):
    """A linear gauge for displaying an individual metric."""

    def __init__(self, master, name, icon, **kwargs):
        super().__init__(master, fg_color=FRAME_BG_COLOR, corner_radius=10, **kwargs)

        self.name = name  # Store the name for checking
        self.value = 0

        # --- Grid Layout ---
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure((0, 1), weight=0)

        # --- Icon and Name ---
        label_frame = ctk.CTkFrame(self, fg_color="transparent")
        label_frame.grid(row=0, column=0, columnspan=3,
                         sticky="w", padx=15, pady=(10, 5))

        icon_label = ctk.CTkLabel(
            label_frame, text=icon, font=("Segoe UI", 18))
        icon_label.pack(side="left")

        name_label = ctk.CTkLabel(label_frame, text=name, font=(
            "Segoe UI Bold", 16), text_color=TEXT_COLOR)
        name_label.pack(side="left", padx=(10, 0))

        # --- Progress Bar ---
        self.progress_bar = ctk.CTkProgressBar(
            self, fg_color="#454D6E", progress_color=ACCENT_COLOR,
            height=8, corner_radius=4
        )
        self.progress_bar.set(0)
        self.progress_bar.grid(row=1, column=0, columnspan=2,
                               sticky="ew", padx=15, pady=(0, 15))

        # --- Value Label ---
        self.value_label = ctk.CTkLabel(self, text="0.0%", font=(
            "Segoe UI Semibold", 14), text_color="#AAB1C2")
        self.value_label.grid(row=1, column=2, sticky="e",
                              padx=(10, 15), pady=(0, 15))

    def update_value(self, value):
        """Updates the progress bar and value text."""
        self.value = value
        self.progress_bar.set(value / 100)

        # Update color based on value
        if value > 85:
            color = RED
        elif value > 65:
            color = ORANGE
        else:
            color = GREEN
        self.progress_bar.configure(progress_color=color)

        # Update text, handling temperature differently
        if "Temp" in self.name:
            self.value_label.configure(text=f"{value:.1f}°C")
        else:
            self.value_label.configure(text=f"{value:.1f}%")
