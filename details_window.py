import customtkinter as ctk

class DetailsWindow(ctk.CTkToplevel):
    """
    A custom pop-up window designed to display a list of items,
    such as the top 5 running processes.
    """
    def __init__(self, title, data_list):
        super().__init__()

        self.title(title)
        self.geometry("450x350")
        self.resizable(False, False)
        self.attributes("-topmost", True)

        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(padx=10, pady=10, expand=True, fill="both")
        main_frame.grid_columnconfigure(0, weight=1)

        # Create a scrollable frame to hold the list
        scrollable_frame = ctk.CTkScrollableFrame(main_frame, label_text=title, label_font=("Segoe UI Bold", 16))
        scrollable_frame.pack(expand=True, fill="both")

        # Display the data
        if not data_list:
            label = ctk.CTkLabel(scrollable_frame, text="No process data available.", font=("Segoe UI", 14))
            label.pack(pady=10)
        else:
            for item_name, item_value in data_list:
                item_frame = ctk.CTkFrame(scrollable_frame, fg_color="#3D4460")
                item_frame.pack(fill="x", pady=5, padx=5)
                
                name_label = ctk.CTkLabel(item_frame, text=item_name, font=("Segoe UI", 14), anchor="w")
                name_label.pack(side="left", padx=10, pady=5)
                
                value_label = ctk.CTkLabel(item_frame, text=f"{item_value:.1f}%", font=("Segoe UI Bold", 14), anchor="e")
                value_label.pack(side="right", padx=10, pady=5)

        ok_button = ctk.CTkButton(main_frame, text="Close", command=self.destroy, width=100)
        ok_button.pack(pady=10)

