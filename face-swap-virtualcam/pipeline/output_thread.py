import threading
import queue
import logging
import cv2
import time

logger = logging.getLogger("OutputThread")

class OutputThread(threading.Thread):
    def __init__(self, config, result_queue: queue.Queue, ui_callback):
        super().__init__(daemon=True)
        self.config = config
        self.result_queue = result_queue
        self.running = False
        self.ui_callback = ui_callback # Funzione CTk per la Live Preview a sinistra
        
        self.width = self.config.get("virtual_cam_width", 1280)
        self.height = self.config.get("virtual_cam_height", 720)
        self.fps = self.config.get("virtual_cam_fps", 30)

    def start_output(self):
        self.running = True
        self.start()

    def stop_output(self):
        self.running = False

    def run(self):
        logger.info("Avviando OutputThread (PyVirtualCam + GUI Update)")
        
        # L'import di pyvirtualcam fallirebbe prima di averlo installato su pip
        try:
            import pyvirtualcam
        except ImportError:
            logger.error("pyvirtualcam non installato. Fallback senza telecamera virtuale.")
            self._run_fallback()
            return

        try:
            # OBS VirtualCam su Windows
            with pyvirtualcam.Camera(width=self.width, height=self.height, fps=self.fps) as cam:
                logger.info(f"Costruito Virtual Camera stream: {cam.device}")
                
                frame_count = 0
                while self.running:
                    try:
                        frame = self.result_queue.get(timeout=0.1)
                        
                        # RGB needed per VirtualCam e GUI PIL
                        if frame is not None:
                            frame_count += 1
                            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                            
                            if (rgb_frame.shape[1] != self.width) or (rgb_frame.shape[0] != self.height):
                                rgb_frame = cv2.resize(rgb_frame, (self.width, self.height))
                                
                            # MANDA A OBS / DISCORD ecc. FULL 30 FPS
                            cam.send(rgb_frame)
                            
                            # MANDA LA COPIA PICCOLA ALLA GUI PER IL PREVIEW a 15 FPS (evita lag su Tkinter)
                            if self.ui_callback and frame_count % 2 == 0:
                                self.ui_callback(rgb_frame)
                                
                    except queue.Empty:
                        pass
        except Exception as e:
            logger.error(f"Errore di inizializzazione VirtualCam: {e}")
            # self.running RIMANE TRUE così il fallback può girare
            self._run_fallback()

    def _run_fallback(self):
        logger.warning("Usando il Loop di Fallback (Solo aggiornamento GUI).")
        frame_time = 1.0 / self.fps
        while self.running:
            try:
                start_time = time.time()
                frame = self.result_queue.get(timeout=0.1)
                if frame is not None and self.ui_callback:
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    self.ui_callback(rgb_frame)
                    
                elapsed = time.time() - start_time
                if (frame_time - elapsed) > 0:
                    time.sleep(frame_time - elapsed)
            except queue.Empty:
                pass
            except Exception as e:
                logger.error(f"Fallback crash: {e}")
                
        logger.info("OutputThread terminato.")
