import customtkinter as ctk
import logging
from PIL import Image, ImageTk
import numpy as np
import cv2
from core.config import AppConfig

logger = logging.getLogger("PreviewPanel")

class PreviewPanel(ctk.CTkFrame):
    def __init__(self, master, config: AppConfig):
        super().__init__(master)
        self.config = config
        
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Header professionale
        self.lbl_title = ctk.CTkLabel(
            self, 
            text="AI LIVE MONITOR", 
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#3B8ED0"
        )
        self.lbl_title.grid(row=0, column=0, pady=(10, 0), sticky="n")
        
        self.preview_container = ctk.CTkFrame(self, fg_color="transparent")
        self.preview_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        self.preview_container.grid_rowconfigure(0, weight=1)
        self.preview_container.grid_columnconfigure(0, weight=1)
        self.preview_container.grid_columnconfigure(1, weight=1)
        
        # CAMERA (Frame Sinistro)
        self.frame_camera = ctk.CTkFrame(self.preview_container, border_width=2, border_color="#333333")
        self.frame_camera.grid(row=0, column=0, padx=5, sticky="nsew")
        
        self.lbl_camera = ctk.CTkLabel(self.frame_camera, text="Webcam Offline", text_color="gray")
        self.lbl_camera.pack(expand=True, fill="both")
        
        # SORGENTE (Frame Destro)
        self.frame_source = ctk.CTkFrame(self.preview_container, border_width=2, border_color="#333333")
        self.frame_source.grid(row=0, column=1, padx=5, sticky="nsew")
        
        self.lbl_source = ctk.CTkLabel(self.frame_source, text="Target Face Not Set", text_color="gray")
        self.lbl_source.pack(expand=True, fill="both")
        
        # Cache per le immagini (Evita il Garbage Collection aggressivo di Tkinter)
        self._tk_cam_image = None
        self._tk_source_image = None

    def update_camera_frame(self, rgb_array: np.ndarray):
        """Riceve un frame RGB e lo renderizza nel widget correggendo l'aspect ratio."""
        try:
            # Ottieni dimensioni del widget per il resize
            w = self.frame_camera.winfo_width()
            h = self.frame_camera.winfo_height()
            
            if w < 10 or h < 10: return

            # Resize iper-veloce in OpenCV
            resized = cv2.resize(rgb_array, (w, h), interpolation=cv2.INTER_LINEAR)
            
            # Conversione PIL -> ImageTk (Metodo più veloce per Tkinter)
            img = Image.fromarray(resized)
            self._tk_cam_image = ImageTk.PhotoImage(image=img)
            
            self.lbl_camera.configure(image=self._tk_cam_image, text="")
        except Exception as e:
            logger.error(f"UI Camera Render Error: {e}")

    def update_source_frame(self, pil_image: Image.Image):
        """Aggiorna la miniatura della faccia target a destra."""
        try:
            # Usiamo CTkImage qui perché è una statica, non deve girare a 30fps
            self._tk_source_image = ctk.CTkImage(
                light_image=pil_image, 
                dark_image=pil_image, 
                size=(300, 300)
            )
            self.lbl_source.configure(image=self._tk_source_image, text="")
        except Exception as e:
            logger.error(f"UI Source Render Error: {e}")
