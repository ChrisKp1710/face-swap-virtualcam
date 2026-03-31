import customtkinter as ctk
import logging
from PIL import Image, ImageTk, ImageOps
import numpy as np
import cv2
from core.config import AppConfig

logger = logging.getLogger("PreviewPanel")

class PreviewPanel(ctk.CTkFrame):
    def __init__(self, master, config: AppConfig):
        super().__init__(master, fg_color="transparent")
        self.config = config
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Container principale asimmetrico
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.grid(row=0, column=0, sticky="nsew")
        
        # LAYOUT RIGIDO: 60% | 10% | 30%
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=60, uniform="preview_group") 
        self.main_container.grid_columnconfigure(1, weight=10, uniform="preview_group")
        self.main_container.grid_columnconfigure(2, weight=30, uniform="preview_group")
        
        # 1. CARD WEBCAM (MASTER)
        # Impostiamo width/height minimi ma blocchiamo la propagazione
        self.cam_card = ctk.CTkFrame(self.main_container, corner_radius=30, fg_color="#1A1A1A", border_width=2, border_color="#2B2B2B")
        self.cam_card.grid(row=0, column=0, sticky="nsew", padx=(20, 10), pady=40)
        self.cam_card.pack_propagate(False) # <--- FONDAMENTALE: La card NON si espande per l'immagine
        
        self.lbl_camera = ctk.CTkLabel(self.cam_card, text="")
        self.lbl_camera.pack(expand=True, fill="both")
        
        # 2. INDICATORE
        self.flow_indicator = ctk.CTkLabel(
            self.main_container, 
            text="→", 
            font=ctk.CTkFont(size=45, weight="bold"), 
            text_color="#3B8ED0"
        )
        self.flow_indicator.grid(row=0, column=1)
        
        # 3. CARD SOURCE (MASTER)
        self.source_card = ctk.CTkFrame(self.main_container, corner_radius=30, fg_color="#1A1A1A", border_width=2, border_color="#2B2B2B")
        self.source_card.grid(row=0, column=2, sticky="nsew", padx=(10, 20), pady=80)
        self.source_card.pack_propagate(False) # <--- FONDAMENTALE: La card resta della dimensione decisa dalla griglia
        
        self.lbl_source = ctk.CTkLabel(self.source_card, text="")
        self.lbl_source.pack(expand=True, fill="both")
        
        self._ctk_cam_img = None
        self._ctk_source_img = None

    def _smart_crop_resize(self, pil_img: Image.Image, target_w: int, target_h: int) -> Image.Image:
        """Ritaglio centrale per riempire lo spazio assegnato."""
        # Se il widget è appena stato creato, potrebbe avere dimensioni 1x1
        if target_w < 10 or target_h < 10: return pil_img
        return ImageOps.fit(pil_img, (target_w, target_h), method=Image.Resampling.LANCZOS)

    def update_camera_frame(self, rgb_array: np.ndarray):
        """Si adatta alla dimensione della Card senza mai allargarla."""
        try:
            # Prende la dimensione REALE che la griglia ha dato alla card
            w_target = self.cam_card.winfo_width() - 4 # Sottraiamo bordi
            h_target = self.cam_card.winfo_height() - 4
            
            if w_target < 50: return

            pil_img = Image.fromarray(rgb_array)
            filled_img = self._smart_crop_resize(pil_img, w_target, h_target)
            
            # Crea l'immagine della dimensione ESATTA della card
            self._ctk_cam_img = ctk.CTkImage(light_image=filled_img, dark_image=filled_img, size=(w_target, h_target))
            self.lbl_camera.configure(image=self._ctk_cam_img)
            
        except Exception as e:
            logger.error(f"UI Cam Resize Error: {e}")

    def update_source_frame(self, pil_image: Image.Image):
        """Si adatta alla dimensione della Card Source."""
        try:
            w_target = self.source_card.winfo_width() - 4
            h_target = self.source_card.winfo_height() - 4
            
            if w_target < 50: return

            filled_img = self._smart_crop_resize(pil_image, w_target, h_target)
            
            self._ctk_source_img = ctk.CTkImage(light_image=filled_img, dark_image=filled_img, size=(w_target, h_target))
            self.lbl_source.configure(image=self._ctk_source_img)
        except Exception as e:
            logger.error(f"UI Source Resize Error: {e}")
