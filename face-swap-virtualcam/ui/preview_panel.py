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
            text="REAL-TIME AI PROCESSING ENGINE", 
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#3B8ED0"
        )
        self.lbl_title.grid(row=0, column=0, pady=(10, 5), sticky="n")
        
        # Container principale con 3 colonne parallele
        self.preview_container = ctk.CTkFrame(self, fg_color="transparent")
        self.preview_container.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
        
        self.preview_container.grid_rowconfigure(0, weight=1)
        self.preview_container.grid_columnconfigure(0, weight=45) # CAM
        self.preview_container.grid_columnconfigure(1, weight=10) # ARROW
        self.preview_container.grid_columnconfigure(2, weight=45) # SOURCE
        
        # 1. CAMERA CONTAINER (Identico al source)
        self.frame_camera = ctk.CTkFrame(self.preview_container, border_width=2, border_color="#1f538d", fg_color="#111111")
        self.frame_camera.grid(row=0, column=0, sticky="nsew")
        
        self.lbl_camera = ctk.CTkLabel(self.frame_camera, text="Webcam Off", text_color="#555555")
        self.lbl_camera.pack(expand=True, fill="both", padx=2, pady=2)
        
        # 2. FRECCIA CENTRALE (Visual flow indicator)
        self.arrow_container = ctk.CTkFrame(self.preview_container, fg_color="transparent")
        self.arrow_container.grid(row=0, column=1, sticky="nsew")
        self.lbl_arrow = ctk.CTkLabel(self.arrow_container, text="➜", font=ctk.CTkFont(size=40, weight="bold"), text_color="#3B8ED0")
        self.lbl_arrow.pack(expand=True)
        
        # 3. SOURCE CONTAINER (Identico alla cam)
        self.frame_source = ctk.CTkFrame(self.preview_container, border_width=2, border_color="#1f538d", fg_color="#111111")
        self.frame_source.grid(row=0, column=2, sticky="nsew")
        
        self.lbl_source = ctk.CTkLabel(self.frame_source, text="No Target Face", text_color="#555555")
        self.lbl_source.pack(expand=True, fill="both", padx=2, pady=2)
        
        # Cache oggetti CTkImage per evitare lag di instanziamento continuo
        self._ctk_cam_img = None
        self._ctk_source_img = None

    def update_camera_frame(self, rgb_array: np.ndarray):
        """Renderizza il frame mantenendo le proporzioni (Letterboxing)."""
        try:
            # Dimensioni widget target
            w_target = self.frame_camera.winfo_width() - 4
            h_target = self.frame_camera.winfo_height() - 4
            if w_target < 10 or h_target < 10: return

            # Calcolo proporzioni originali (1920/1080 = 1.77)
            h_orig, w_orig = rgb_array.shape[:2]
            aspect_orig = w_orig / h_orig
            aspect_target = w_target / h_target

            # Ridimensionamento proporzionale (Letterbox intelligente)
            if aspect_orig > aspect_target: # Più larga del widget
                w_new = w_target
                h_new = int(w_target / aspect_orig)
            else: # Più stretta del widget
                h_new = h_target
                w_new = int(h_target * aspect_orig)

            # Resize OpenCV (velocissimo)
            resized = cv2.resize(rgb_array, (w_new, h_new), interpolation=cv2.INTER_LINEAR)
            
            # Conversione PIL
            pil_img = Image.fromarray(resized)
            
            # Aggiornamento CTkImage senza ricreare l'oggetto se possibile (Fix Warning HighDPI)
            # Nota: CTkLabel accetta CTkImage per supportare il ridimensionamento HighDPI nativo
            self._ctk_cam_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(w_new, h_new))
            self.lbl_camera.configure(image=self._ctk_cam_img, text="")
            
        except Exception as e:
            logger.error(f"UI Camera Render Error: {e}")

    def update_source_frame(self, pil_image: Image.Image):
        """Aggiorna la miniatura della faccia target mantenendo l'aspetto."""
        try:
            w_target = self.frame_source.winfo_width() - 10
            h_target = self.frame_source.winfo_height() - 10
            
            # Anche qui facciamo un resize intelligente
            pil_image.thumbnail((w_target, h_target), Image.Resampling.LANCZOS)
            
            self._ctk_source_img = ctk.CTkImage(
                light_image=pil_image, 
                dark_image=pil_image, 
                size=(pil_image.width, pil_image.height)
            )
            self.lbl_source.configure(image=self._ctk_source_img, text="")
        except Exception as e:
            logger.error(f"UI Source Render Error: {e}")
