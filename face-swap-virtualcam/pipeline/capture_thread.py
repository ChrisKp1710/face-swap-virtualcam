import cv2
import threading
import queue
import time
import logging

logger = logging.getLogger("CaptureThread")

class CaptureThread(threading.Thread):
    def __init__(self, config, output_queue: queue.Queue):
        super().__init__(daemon=True)
        self.config = config
        self.output_queue = output_queue
        self.cam_id = self.config.get("webcam_id", 0)
        self.fps_target = self.config.get("virtual_cam_fps", 30)
        self.running = False
        self.cap = None

    def start_capture(self):
        self.running = True
        self.start()

    def stop_capture(self):
        self.running = False
        # IMPORTANTE: Su Windows non fare MAI cap.release() dal main thread,
        # altrimenti causa deadlock di 3 secondi o crash se il thread bkg sta leggendo.
        # Lasciamo che sia il run() a chiuderlo uscendo dal ciclo while.

    def run(self):
        logger.info(f"Avviando CaptureThread. Cerco la webcam fisica...")
        
        # Testiamo dinamicamente più ID (0, 1, 2) per trovare quella reale
        # L'ID 0 potrebbe essere occupato o assegnato ad una virtual cam fantasma.
        for test_id in [self.cam_id, 0, 1, 2]:
            self.cap = cv2.VideoCapture(test_id, cv2.CAP_DSHOW)
            if self.cap.isOpened():
                logger.info(f"SUCCESS: Webcam trovata all'ID {test_id} (DirectShow)")
                break
            
            # Fallback MSMF
            self.cap = cv2.VideoCapture(test_id)
            if self.cap.isOpened():
                logger.info(f"SUCCESS: Webcam trovata all'ID {test_id} (Base)")
                break

        if not self.cap or not self.cap.isOpened():
            logger.error("Impossibile aprire NESSUNA webcam! Controlla i permessi di Windows o riavvia.")
            self.running = False
            return
            
        # Forza la risoluzione (molte webcam potrebbero non rispettarla nativamente)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.get("virtual_cam_width", 1280))
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.get("virtual_cam_height", 720))
        self.cap.set(cv2.CAP_PROP_FPS, self.fps_target)

        while self.running:
            ret, frame = self.cap.read()
            
            if ret:
                # Svuota buffer vecchio se pieno per non avere lag (LIFO effect)
                if self.output_queue.full():
                    try:
                        self.output_queue.get_nowait()
                    except queue.Empty:
                        pass
                
                self.output_queue.put(frame)
            else:
                logger.warning("Frame perso durante la lettura della webcam")
                time.sleep(0.01)

        if self.cap and self.cap.isOpened():
            self.cap.release()
            
        logger.info("CaptureThread arrestato con successo.")
