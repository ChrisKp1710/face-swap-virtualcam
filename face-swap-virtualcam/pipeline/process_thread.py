import threading
import queue
import time
import logging
import cv2

logger = logging.getLogger("ProcessThread")

class ProcessThread(threading.Thread):
    def __init__(self, config, input_queue: queue.Queue, output_queue: queue.Queue):
        super().__init__(daemon=True)
        self.config = config
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.running = False
        self.effect_enabled = False
        
        # [Placeholder per motori ONNX (InsightFace e CodeFormer) - Fase 4 e 4.5]
        self.face_swapper = None 
        self.face_enhancer = None

    def start_process(self):
        self.running = True
        self.start()

    def stop_process(self):
        self.running = False

    def toggle_effect(self, state: bool):
        self.effect_enabled = state
        logger.info(f"Effetto Face-Swap impostato a: {state}")

    def run(self):
        logger.info("Avviando ProcessThread per inferenza AI")
        while self.running:
            try:
                # Prende l'ultimo frame dalla telecamera (Timeout corto evita stalli thread-freeze)
                frame = self.input_queue.get(timeout=0.1)
                
                # SE L'EFFETTO È DISATTIVATO O SORGENTE MANCANTE -> Passa l'immagine originale
                if not self.effect_enabled:
                    processed_frame = frame.copy()
                else:
                    # ---> FASE 4 START: Qui implementeremo il Core AI (Detection -> Swap -> Enhance)
                    
                    # (Placeholder temporaneo in attesa dell'integrazione InsightFace/DirectML)
                    # es: processed_frame = self.face_swapper.swap(frame, source_face)
                    
                    # Momentaneamente solo una copia
                    processed_frame = frame.copy()
                    
                # Scartiamo output vecchi per mantenere lo streaming in tempo reale perfetto
                if self.output_queue.full():
                    try:
                        self.output_queue.get_nowait()
                    except queue.Empty:
                        pass
                        
                self.output_queue.put(processed_frame)

            except queue.Empty:
                pass
            except Exception as e:
                logger.error(f"Errore gravissimo nel loop AI: {e}", exc_info=True)

        logger.info("ProcessThread arrestato.")
