import customtkinter as ctk
import logging
from tkinter import filedialog

logger = logging.getLogger("SettingsPanel")

class SettingsPanel(ctk.CTkFrame):
    def __init__(self, master, config, on_change_callback):
        super().__init__(master)
        self.config = config
        self.on_change = on_change_callback

        # Make rows stretch properly
        for i in range(10):
            self.grid_rowconfigure(i, weight=0)

        # Title
        self.lbl_title = ctk.CTkLabel(self, text="Settings & Controls", font=ctk.CTkFont(size=18, weight="bold"))
        self.lbl_title.grid(row=0, column=0, pady=(10, 20), sticky="n")

        # 1. Main Controls
        self.btn_load_source = ctk.CTkButton(self, text="Load Source Photo", command=self.load_source_photo)
        self.btn_load_source.grid(row=1, column=0, pady=10, padx=20, sticky="ew")

        self.btn_toggle_cam = ctk.CTkButton(self, text="Start Webcam", fg_color="green", hover_color="darkgreen", command=self.toggle_cam)
        self.btn_toggle_cam.grid(row=2, column=0, pady=10, padx=20, sticky="ew")

        self.btn_toggle_effect = ctk.CTkButton(self, text="Enable Swap Effect", fg_color="gray", command=self.toggle_effect)
        self.btn_toggle_effect.grid(row=3, column=0, pady=10, padx=20, sticky="ew")

        # 2. Hardware Provider Dropdown
        self.lbl_provider = ctk.CTkLabel(self, text="AI Hardware Provider:")
        self.lbl_provider.grid(row=4, column=0, pady=(20, 0), padx=20, sticky="w")
        self.combo_provider = ctk.CTkComboBox(
            self, 
            values=self.config.get("providers", ["CPUExecutionProvider"]),
            command=self.provider_changed
        )
        self.combo_provider.grid(row=5, column=0, pady=5, padx=20, sticky="ew")
        
        # 3. Sliders & Advanced Settings
        self.lbl_enhance = ctk.CTkLabel(self, text="Face Enhancement Weight:")
        self.lbl_enhance.grid(row=6, column=0, pady=(20, 0), padx=20, sticky="w")
        self.slider_enhance = ctk.CTkSlider(self, from_=0, to=1, command=self.enhance_changed)
        self.slider_enhance.set(self.config.get("face_enhancement_weight", 0.5))
        self.slider_enhance.grid(row=7, column=0, pady=5, padx=20, sticky="ew")

        # Status Label
        self.lbl_status = ctk.CTkLabel(self, text="Status: IDLE", text_color="gray")
        self.lbl_status.grid(row=8, column=0, pady=20, padx=20, sticky="s")

    def load_source_photo(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.webp")]
        )
        if file_path:
            logger.info(f"Loaded source photo: {file_path}")
            self.on_change("source_photo_path", file_path)
            # Notify the main app to update preview

    def toggle_cam(self):
        # Placeholder for start/stop cam
        current_text = self.btn_toggle_cam.cget("text")
        if current_text == "Start Webcam":
            self.btn_toggle_cam.configure(text="Stop Webcam", fg_color="red", hover_color="darkred")
            self.lbl_status.configure(text="Status: CAM RUNNING", text_color="green")
            self.on_change("cam_running", True)
        else:
            self.btn_toggle_cam.configure(text="Start Webcam", fg_color="green", hover_color="darkgreen")
            self.lbl_status.configure(text="Status: IDLE", text_color="gray")
            self.on_change("cam_running", False)

    def toggle_effect(self):
        current_text = self.btn_toggle_effect.cget("text")
        if current_text == "Enable Swap Effect":
            self.btn_toggle_effect.configure(text="Disable Swap Effect", fg_color="blue")
            self.on_change("effect_enabled", True)
        else:
            self.btn_toggle_effect.configure(text="Enable Swap Effect", fg_color="gray")
            self.on_change("effect_enabled", False)
            
    def provider_changed(self, choice):
        self.on_change("active_provider", choice)
        
    def enhance_changed(self, value):
        # Optional: round properly
        self.on_change("face_enhancement_weight", round(value, 2))
