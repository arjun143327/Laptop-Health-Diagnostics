import customtkinter as ctk


class GaugeWidget(ctk.CTkFrame):
    """
    A custom widget to display a system metric with a title, value, and progress bar.
    """

    def __init__(self, master, name, color, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        self.name = name
        self.color = color

        # Configure grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Metric title
        self.title_label = ctk.CTkLabel(
            self,
            text=self.name,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#566573"
        )
        self.title_label.grid(row=0, column=0, sticky="s", pady=(0, 5))

        # Metric value label
        self.value_label = ctk.CTkLabel(
            self,
            text="--",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#2C3E50"
        )
        self.value_label.grid(row=1, column=0, sticky="n")

        # Progress bar to act as a gauge
        self.progress_bar = ctk.CTkProgressBar(
            self,
            orientation="horizontal",
            progress_color=self.color,
            fg_color="#EAECEE"
        )
        self.progress_bar.set(0)
        self.progress_bar.grid(
            row=2, column=0, sticky="ew", padx=15, pady=(5, 0))

    def update_value(self, value, display_text):
        """
        Updates the gauge with a new value.
        - value: A number between 0 and 100 for the progress bar.
        - display_text: The string to show as the metric value (e.g., "55%").
        """
        if value is None:
            self.value_label.configure(text="N/A")
            self.progress_bar.set(0)
        else:
            self.value_label.configure(text=display_text)
            self.progress_bar.set(value / 100.0)
