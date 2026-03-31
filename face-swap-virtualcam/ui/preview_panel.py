import customtkinter as ctk
import logging
from PIL import Image
import numpy as np

logger = logging.getLogger("PreviewPanel")

class PreviewPanel(ctk.CTkFrame):
    def __init__(self, master, config):
        super().__init__(master)
        self.config = config
        
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.lbl_title = ctk.CTkLabel(self, text="Monitor Live", font=ctk.CTkFont(size=20, weight="bold"))
        self.lbl_title.grid(row=0, column=0, pady=(10, 0), sticky="n")
        
        self.preview_container = ctk.CTkFrame(self, fg_color="transparent")
        self.preview_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        self.preview_container.grid_rowconfigure(0, weight=1)
        self.preview_container.grid_columnconfigure(0, weight=1)
        self.preview_container.grid_columnconfigure(1, weight=1)
        
        # CAMERA (Frame Sinistro)
        self.frame_camera = ctk.CTkFrame(self.preview_container)
        self.frame_camera.grid(row=0, column=0, padx=5, sticky="nsew")
        
        self.lbl_camera = ctk.CTkLabel(self.frame_camera, text="[Webcam Offline]")
        self.lbl_camera.pack(expand=True, fill="both")
        
        # SORGENTE (Frame Destro)
        self.frame_source = ctk.CTkFrame(self.preview_container)
        self.frame_source.grid(row=0, column=1, padx=5, sticky="nsew")
        
        self.lbl_source = ctk.CTkLabel(self.frame_source, text="[Foto Sorgente Vuota]")
        self.lbl_source.pack(expand=True, fill="both")
        
        self.current_cam_image = None
        self.current_source_image = None

    def update_camera_frame(self, rgb_ndarray):
        # Riceviamo frame RGB numpy convertiti da OpenCV
        try:
            h, w, c = rgb_ndarray.shape
            
            # Mantieni form-factor adattandolo al widget in real-time
            widget_w = self.frame_camera.winfo_width()
            widget_h = self.frame_camera.winfo_height()
            
            if widget_w <= 1 or widget_h <= 1: 
                return
                
            img = Image.fromarray(rgb_ndarray)
            
            # Non usiamo thumbnail ma un CTkImage col size dinamico
            self.current_cam_image = ctk.CTkImage(light_image=img, dark_image=img, size=(widget_w, widget_h))
            self.lbl_camera.configure(image=self.current_cam_image, text="")
        except Exception as e:
            logger.error(f"Errore UI Render: {e}")

    def update_source_frame(self, pil_image: Image.Image):
        try:
            self.current_source_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(250, 250))
            self.lbl_source.configure(image=self.current_source_image, text="")
        except Exception as e:
            logger.error(f"Errore caricamento miniatura: {e}")
