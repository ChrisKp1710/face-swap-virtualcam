import customtkinter as ctk
import logging
import queue
from PIL import Image

from .preview_panel import PreviewPanel
from .settings_panel import SettingsPanel
from pipeline.capture_thread import CaptureThread
from pipeline.process_thread import ProcessThread
from pipeline.output_thread import OutputThread

logger = logging.getLogger("FaceSwapApp")

class FaceSwapApp(ctk.CTk):
    def __init__(self, config):
        super().__init__()
        
        ctk.set_appearance_mode(config.get("ui_theme", "dark"))
        ctk.set_default_color_theme(config.get("ui_color", "blue"))
        
        self.config = config
        self.title("Real-Time Face-Swap Virtual Cam")
        self.geometry("1100x700")
        self.minsize(900, 600)
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=7)
        self.grid_columnconfigure(1, weight=3)
        
        self.preview_panel = PreviewPanel(self, config)
        self.preview_panel.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        self.settings_panel = SettingsPanel(self, config, self.on_settings_change)
        self.settings_panel.grid(row=0, column=1, padx=(0, 10), pady=10, sticky="nsew")
        
        self.capture_queue = queue.Queue(maxsize=2)
        self.process_queue = queue.Queue(maxsize=2)
        
        self.capture_thread = None
        self.process_thread = None
        self.output_thread = None
        
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def _start_threads(self):
        self._stop_threads()
        
        # Pulisci le code
        with self.capture_queue.mutex:
            self.capture_queue.queue.clear()
        with self.process_queue.mutex:
            self.process_queue.queue.clear()
            
        # Ricrea le istanze dei thread (in Python i thread non possono ripartire se stoppati)
        self.capture_thread = CaptureThread(self.config, self.capture_queue)
        self.process_thread = ProcessThread(self.config, self.capture_queue, self.process_queue)
        self.output_thread = OutputThread(self.config, self.process_queue, self.update_gui_preview)
        
        self.process_thread.toggle_effect(self.config.get("effect_enabled", False))
        
        self.output_thread.start_output()
        self.process_thread.start_process()
        self.capture_thread.start_capture()

    def _stop_threads(self):
        if self.capture_thread: self.capture_thread.stop_capture()
        if self.process_thread: self.process_thread.stop_process()
        if self.output_thread: self.output_thread.stop_output()

    def update_gui_preview(self, rgb_frame):
        self.after(0, self.preview_panel.update_camera_frame, rgb_frame)
        
    def on_settings_change(self, key, value):
        logger.info(f"Setting applicato -> {key} = {value}")
        self.config[key] = value
        
        if key == "cam_running":
            if value:
                self._start_threads()
            else:
                self._stop_threads()
                
        elif key == "effect_enabled":
            if self.process_thread:
                self.process_thread.toggle_effect(value)
            
        elif key == "source_photo_path":
            try:
                img = Image.open(value).convert("RGB")
                self.preview_panel.update_source_frame(img)
            except Exception as e:
                logger.error(f"Errore foto sorgente: {e}")

    def on_closing(self):
        logger.info("Chiusura in corso...")
        self._stop_threads()
        self.destroy()
