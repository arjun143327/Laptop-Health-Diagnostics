import customtkinter as ctk
import math

class CircularProgressGauge(ctk.CTkFrame):
    """
    A circular progress gauge that now smoothly animates to new values.
    """
    def __init__(self, parent, size=200, **kwargs):
        super().__init__(parent, **kwargs)
        self.size = size
        self.configure(fg_color="transparent")

        self.canvas = ctk.CTkCanvas(self, width=size, height=size, bg="black", highlightthickness=0)
        self.canvas.pack()

        # --- NEW: Animation state variables ---
        self.current_value = 0.0
        self.target_value = 0.0
        self.animation_job = None # To manage the animation loop

        self.status_text = "Initializing..."
        self.status_color = "#AAB1C2"
        self.draw()

    def update_value(self, value, text, color):
        """
        This method now sets the target for the animation and starts it.
        It no longer draws directly.
        """
        self.target_value = value
        self.status_text = text
        self.status_color = color
        
        # Cancel any previous animation job and start a new one
        if self.animation_job:
            self.after_cancel(self.animation_job)
        
        self._animate_step()

    def _animate_step(self):
        """The core animation loop. Runs every few milliseconds."""
        # Calculate the difference between current and target
        distance = self.target_value - self.current_value
        
        # If we are very close to the target, just jump to it and stop
        if abs(distance) < 0.1:
            self.current_value = self.target_value
            self.draw()
            return

        # --- The Easing Algorithm ---
        # Move a fraction of the remaining distance (e.g., 10%) each step.
        # This creates a smooth "ease-out" effect where it starts fast and slows down.
        self.current_value += distance * 0.1
        
        self.draw() # Redraw the gauge at the new intermediate position
        
        # Schedule the next animation step to run in 15ms (~66 FPS)
        self.animation_job = self.after(15, self._animate_step)

    def draw(self):
        """Draws the gauge on the canvas based on the current_value."""
        self.canvas.delete("all")
        self.canvas.configure(bg="#2C324A") # Match frame background

        # Draw the background track
        self.canvas.create_arc(10, 10, self.size-10, self.size-10, start=90, extent=359.9, 
                               style="arc", outline="#3D4460", width=15)

        # Draw the progress arc
        if self.current_value > 0:
            self.canvas.create_arc(10, 10, self.size-10, self.size-10, start=90, 
                                   extent=-(self.current_value / 100 * 360),
                                   style="arc", outline=self.status_color, width=16)

        # Draw the text in the center
        self.canvas.create_text(self.size/2, self.size/2 - 10, text=f"{self.current_value:.1f}", 
                                font=("Segoe UI Bold", 40), fill=self.status_color)
        self.canvas.create_text(self.size/2, self.size/2 + 30, text=self.status_text, 
                                font=("Segoe UI", 16), fill=self.status_color)


class LinearGaugeWidget(ctk.CTkFrame):
    """A linear progress bar for individual metrics."""
    # This widget does not need animation for now to keep CPU usage low.
    # It remains unchanged.
    def __init__(self, parent, name, icon):
        super().__init__(parent, fg_color="#3D4460", corner_radius=8)
        self.name = name
        self.icon = icon

        self.grid_columnconfigure(1, weight=1)
        
        icon_label = ctk.CTkLabel(self, text=self.icon, font=("Segoe UI", 24))
        icon_label.grid(row=0, column=0, rowspan=2, padx=15, pady=10)

        name_label = ctk.CTkLabel(self, text=self.name, font=("Segoe UI", 14), text_color="#AAB1C2")
        name_label.grid(row=0, column=1, sticky="w", padx=10)
        
        self.progress_bar = ctk.CTkProgressBar(self, orientation="horizontal", progress_color="#4A90E2")
        self.progress_bar.set(0)
        self.progress_bar.grid(row=1, column=1, sticky="ew", padx=10, pady=(0, 10))

        self.value_label = ctk.CTkLabel(self, text="0.0%", font=("Segoe UI Bold", 16), text_color="#FFFFFF")
        self.value_label.grid(row=0, column=2, rowspan=2, padx=15, pady=10)

    def update_value(self, value):
        self.progress_bar.set(value / 100)
        self.value_label.configure(text=f"{value:.1f}%")

        if value > 85:
            self.progress_bar.configure(progress_color="#E94B3C")
        elif value > 60:
            self.progress_bar.configure(progress_color="#F7A02B")
        else:
            self.progress_bar.configure(progress_color="#2CC990")

