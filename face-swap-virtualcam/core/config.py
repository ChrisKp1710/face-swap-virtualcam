from dataclasses import dataclass, field
from typing import List, Optional
import json
from pathlib import Path
import logging

logger = logging.getLogger("Config")

@dataclass
class AppConfig:
    # Directory & Paths
    base_dir: Path = Path(__file__).parent.parent
    models_dir: str = "models"
    
    # Camera Settings
    webcam_id: int = 0
    virtual_cam_width: int = 1920
    virtual_cam_height: int = 1080
    virtual_cam_fps: int = 60
    
    # AI Settings
    providers: List[str] = field(default_factory=lambda: ["DmlExecutionProvider", "CPUExecutionProvider"])
    active_provider: Optional[str] = None
    face_enhancement_weight: float = 0.5
    enable_enhancement: bool = True
    enable_color_transfer: bool = True
    enable_temporal_smoothing: bool = True
    
    # UI Settings
    ui_theme: str = "dark"
    ui_color: str = "blue"
    
    # Runtime State (Non salvati su disco)
    cam_running: bool = False
    effect_enabled: bool = False
    source_photo_path: Optional[str] = None

    @classmethod
    def load(cls, path: str = "config.json") -> "AppConfig":
        config_path = Path(path)
        if config_path.exists():
            try:
                with open(config_path, "r") as f:
                    data = json.load(f)
                    # Filtra solo i campi definiti nella dataclass
                    valid_fields = {k: v for k, v in data.items() if k in cls.__dataclass_fields__}
                    return cls(**valid_fields)
            except Exception as e:
                logger.error(f"Errore caricamento config.json: {e}. Uso i default.")
        return cls()

    def save(self, path: str = "config.json"):
        config_path = Path(path)
        # Escludiamo i campi di runtime per non sporcare il file
        exclude = {"base_dir", "cam_running", "effect_enabled", "source_photo_path"}
        data = {k: v for k, v in self.__dict__.items() if k not in exclude}
        try:
            with open(config_path, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Errore salvataggio config.json: {e}")
