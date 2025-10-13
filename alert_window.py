import customtkinter as ctk

class AlertWindow(ctk.CTkToplevel):
    """
    A custom, modern pop-up window for displaying alerts.
    It appears on top of other windows to get the user's attention.
    """
    def __init__(self, title, message):
        super().__init__()

        self.title(title)
        self.geometry("450x170") # A slightly larger window for better text fit
        self.resizable(False, False)
        
        # This crucial line ensures the pop-up appears on top of all other windows
        self.attributes("-topmost", True) 

        # Main frame for padding
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(padx=20, pady=20, expand=True, fill="both")

        # The message label
        self.label = ctk.CTkLabel(main_frame, text=message, font=("Segoe UI", 16), wraplength=400)
        self.label.pack(expand=True, fill="both")

        # The OK button to close the window
        self.ok_button = ctk.CTkButton(main_frame, text="OK", command=self.destroy, width=100)
        self.ok_button.pack(pady=(10, 0))

        # Center the window on the screen
        self.after(100, self.center_window)

    def center_window(self):
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (self.winfo_width() // 2)
        y = (screen_height // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")

