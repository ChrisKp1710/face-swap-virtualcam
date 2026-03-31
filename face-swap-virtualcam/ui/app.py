import customtkinter as ctk
import logging
from typing import Any
from PIL import Image

from .preview_panel import PreviewPanel
from .settings_panel import SettingsPanel
from pipeline.capture_thread import CaptureThread
from pipeline.process_thread import ProcessThread
from pipeline.output_thread import OutputThread
from core.config import AppConfig

logger = logging.getLogger("FaceSwapApp")

class FaceSwapApp(ctk.CTk):
    def __init__(self, config: AppConfig):
        super().__init__()
        
        self.config = config
        
        # UI Setup professionale
        ctk.set_appearance_mode(self.config.ui_theme)
        ctk.set_default_color_theme(self.config.ui_color)
        
        self.title("StreamSwapper | Professional Face-Swap Virtual Cam")
        self.geometry("1100x700")
        self.minsize(1000, 650)
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=7)
        self.grid_columnconfigure(1, weight=3)
        
        self.preview_panel = PreviewPanel(self, self.config)
        self.preview_panel.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        self.settings_panel = SettingsPanel(self, self.config, self.on_settings_change)
        self.settings_panel.grid(row=0, column=1, padx=(0, 10), pady=10, sticky="nsew")
        
        # Pipeline Core
        import queue
        self.capture_queue = queue.Queue(maxsize=2)
        self.process_queue = queue.Queue(maxsize=2)
        
        self.capture_thread = None
        self.process_thread = None
        self.output_thread = None
        
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def _start_threads(self):
        self._stop_threads()
        logger.info("Avvio della pipeline AI...")
        
        # Pulisci le code per evitare frame vecchi (lag di avvio)
        while not self.capture_queue.empty(): self.capture_queue.get()
        while not self.process_queue.empty(): self.process_queue.get()
            
        self.capture_thread = CaptureThread(self.config, self.capture_queue)
        self.process_thread = ProcessThread(self.config, self.capture_queue, self.process_queue)
        self.output_thread = OutputThread(self.config, self.process_queue, self.update_gui_preview)
        
        self.process_thread.toggle_effect(self.config.effect_enabled)
        
        self.output_thread.start_output()
        self.process_thread.start_process()
        self.capture_thread.start_capture()

    def _stop_threads(self):
        if any([self.capture_thread, self.process_thread, self.output_thread]):
            logger.info("Arresto della pipeline...")
            if self.capture_thread: self.capture_thread.stop_capture()
            if self.process_thread: self.process_thread.stop_process()
            if self.output_thread: self.output_thread.stop_output()
            
            # Reset istanze
            self.capture_thread = None
            self.process_thread = None
            self.output_thread = None

    def update_gui_preview(self, rgb_frame):
        # Usiamo after per iniettare l'update nel main thread di Tkinter
        self.after(0, lambda: self.preview_panel.update_camera_frame(rgb_frame))
        
    def on_settings_change(self, key: str, value: Any):
        """Gestore eventi centralizzato per i cambiamenti di configurazione."""
        if hasattr(self.config, key):
            setattr(self.config, key, value)
            logger.debug(f"Config aggiornata: {key} = {value}")
        
        if key == "cam_running":
            if value: self._start_threads()
            else: self._stop_threads()
                
        elif key == "effect_enabled" and self.process_thread:
            self.process_thread.toggle_effect(value)
            
        elif key == "source_photo_path":
            try:
                img = Image.open(value).convert("RGB")
                self.preview_panel.update_source_frame(img)
            except Exception as e:
                logger.error(f"Errore caricamento foto sorgente: {e}")

    def on_closing(self):
        logger.info("Chiusura applicazione in corso...")
        self._stop_threads()
        self.destroy()
