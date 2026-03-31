import customtkinter as ctk
import logging
from tkinter import filedialog
from typing import Callable
from core.config import AppConfig

logger = logging.getLogger("SettingsPanel")

class SettingsPanel(ctk.CTkFrame):
    def __init__(self, master, config: AppConfig, on_change_callback: Callable):
        super().__init__(master)
        self.config = config
        self.on_change = on_change_callback

        self.grid_columnconfigure(0, weight=1)

        # Title
        self.lbl_title = ctk.CTkLabel(
            self, 
            text="CONTROL CENTER", 
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#3B8ED0"
        )
        self.lbl_title.grid(row=0, column=0, pady=(15, 25))

        # --- SECTION: Media ---
        self.media_group = ctk.CTkFrame(self, fg_color="transparent")
        self.media_group.grid(row=1, column=0, sticky="ew", padx=15)
        self.media_group.grid_columnconfigure(0, weight=1)

        self.btn_load_source = ctk.CTkButton(
            self.media_group, 
            text="Select Target Face Image", 
            command=self._load_source_photo,
            height=35
        )
        self.btn_load_source.grid(row=0, column=0, pady=5, sticky="ew")

        self.btn_toggle_cam = ctk.CTkButton(
            self.media_group, 
            text="START WEBCAM", 
            fg_color="#28a745", 
            hover_color="#218838", 
            command=self._toggle_cam,
            height=40,
            font=ctk.CTkFont(weight="bold")
        )
        self.btn_toggle_cam.grid(row=1, column=0, pady=(10, 5), sticky="ew")

        # --- SECTION: AI Settings ---
        self.ai_label = ctk.CTkLabel(self, text="AI Engine Settings", font=ctk.CTkFont(size=13, weight="bold"))
        self.ai_label.grid(row=2, column=0, pady=(25, 5), padx=20, sticky="w")

        self.btn_toggle_effect = ctk.CTkButton(
            self, 
            text="ENABLE FACE-SWAP", 
            fg_color="#6c757d", 
            command=self._toggle_effect,
            height=35
        )
        self.btn_toggle_effect.grid(row=3, column=0, pady=5, padx=15, sticky="ew")

        # Hardware Provider
        self.lbl_provider = ctk.CTkLabel(self, text="Execution Provider:", font=ctk.CTkFont(size=11))
        self.lbl_provider.grid(row=4, column=0, pady=(15, 0), padx=20, sticky="w")
        
        self.combo_provider = ctk.CTkComboBox(
            self, 
            values=self.config.providers,
            command=self._provider_changed
        )
        self.combo_provider.grid(row=5, column=0, pady=5, padx=15, sticky="ew")
        if self.config.active_provider:
            self.combo_provider.set(self.config.active_provider)
        
        # Enhancement Slider
        self.lbl_enhance = ctk.CTkLabel(self, text="Enhancement Intensity:", font=ctk.CTkFont(size=11))
        self.lbl_enhance.grid(row=6, column=0, pady=(15, 0), padx=20, sticky="w")
        
        self.slider_enhance = ctk.CTkSlider(self, from_=0, to=1, command=self._enhance_changed)
        self.slider_enhance.set(self.config.face_enhancement_weight)
        self.slider_enhance.grid(row=7, column=0, pady=5, padx=15, sticky="ew")

        # Status Bar
        self.status_frame = ctk.CTkFrame(self, height=30, fg_color="#222222")
        self.status_frame.grid(row=10, column=0, pady=(30, 0), sticky="ew")
        self.lbl_status = ctk.CTkLabel(self.status_frame, text="STATUS: READY", text_color="#888888", font=ctk.CTkFont(size=10, weight="bold"))
        self.lbl_status.pack(pady=5)

    def _load_source_photo(self):
        file_path = filedialog.askopenfilename(
            title="Select target face image",
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.webp")]
        )
        if file_path:
            self.on_change("source_photo_path", file_path)

    def _toggle_cam(self):
        if not self.config.cam_running:
            self.btn_toggle_cam.configure(text="STOP WEBCAM", fg_color="#dc3545", hover_color="#c82333")
            self.lbl_status.configure(text="STATUS: STREAMING", text_color="#28a745")
            self.on_change("cam_running", True)
        else:
            self.btn_toggle_cam.configure(text="START WEBCAM", fg_color="#28a745", hover_color="#218838")
            self.lbl_status.configure(text="STATUS: READY", text_color="#888888")
            self.on_change("cam_running", False)

    def _toggle_effect(self):
        if not self.config.effect_enabled:
            self.btn_toggle_effect.configure(text="DISABLE FACE-SWAP", fg_color="#007bff", hover_color="#0069d9")
            self.on_change("effect_enabled", True)
        else:
            self.btn_toggle_effect.configure(text="ENABLE FACE-SWAP", fg_color="#6c757d", hover_color="#5a6268")
            self.on_change("effect_enabled", False)
            
    def _provider_changed(self, choice: str):
        self.on_change("active_provider", choice)
        
    def _enhance_changed(self, value: float):
        self.on_change("face_enhancement_weight", round(value, 2))
