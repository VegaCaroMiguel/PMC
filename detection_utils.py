import os
import json
from typing import Dict, Any
from PIL import Image


def read_png_metadata(image_path: str) -> Dict[str, Any]:
    try:
        with Image.open(image_path) as img:
            info = img.info or {}
            return {str(k): (str(v) if not isinstance(v, str) else v) for k, v in info.items()}
    except Exception:
        return {}


def manifest_path_for(image_path: str) -> str:
    base, _ = os.path.splitext(image_path)
    return f"{base}_manifest.json"


def detect_image_status(image_path: str) -> dict:
    result = {
        "image": os.path.basename(image_path),
        "exists": os.path.exists(image_path),
        "ai_generated": False,
        "source": None,
        "details": {}
    }

    if not result["exists"]:
        return result

    meta = read_png_metadata(image_path)
    ai_flag = str(meta.get("AI-Generated", "")).lower() == "true"
    if ai_flag:
        result["ai_generated"] = True
        result["source"] = "png_metadata"
        result["details"] = {k: v for k, v in meta.items() if k.startswith("AI-") or k == "C2PA-Placeholder"}
        return result

    mpath = manifest_path_for(image_path)
    if os.path.exists(mpath):
        with open(mpath, "r", encoding="utf-8") as f:
            manifest = json.load(f)
        if bool(manifest.get("ai_generated", False)):
            result["ai_generated"] = True
            result["source"] = "sidecar_manifest"
            result["details"] = manifest
            return result

    result["source"] = "none"
    return result


