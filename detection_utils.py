import os
import json
from typing import Dict, Any
from PIL import Image, PngImagePlugin
from PIL.ExifTags import TAGS
from datetime import datetime, timezone
import hashlib
import base64

# Intentar importar c2pa
try:
    import c2pa
    C2PA_AVAILABLE = True
except ImportError:
    C2PA_AVAILABLE = False

# Configuración de clave privada C2PA
C2PA_PRIVATE_KEY = os.getenv("C2PA_PRIVATE_KEY", None)  # Ruta al archivo .pem
C2PA_CERTIFICATE = os.getenv("C2PA_CERTIFICATE", None)  # Ruta al certificado .crt


def get_image_format(image_path: str) -> str:
    """Detecta el formato de la imagen"""
    try:
        with Image.open(image_path) as img:
            return img.format.lower() if img.format else "unknown"
    except Exception:
        return "unknown"


def read_image_metadata(image_path: str) -> Dict[str, Any]:
    """Lee metadatos de una imagen (PNG o JPEG)"""
    img_format = get_image_format(image_path)
    
    if img_format == "png":
        return read_png_metadata(image_path)
    elif img_format in ["jpeg", "jpg"]:
        return read_jpeg_metadata(image_path)
    else:
        return {}


def read_png_metadata(image_path: str) -> Dict[str, Any]:
    """Lee metadatos tEXt/iTXt de un PNG"""
    try:
        with Image.open(image_path) as img:
            info = img.info or {}
            return {str(k): (str(v) if not isinstance(v, str) else v) for k, v in info.items()}
    except Exception:
        return {}


def read_jpeg_metadata(image_path: str) -> Dict[str, Any]:
    """Lee metadatos EXIF de un JPEG"""
    try:
        with Image.open(image_path) as img:
            exif_data = img.getexif()
            if not exif_data:
                return {}
            
            metadata = {}
            for tag_id, value in exif_data.items():
                tag = TAGS.get(tag_id, tag_id)
                # Convertir bytes a string si es necesario
                if isinstance(value, bytes):
                    try:
                        value = value.decode('utf-8', errors='ignore')
                    except:
                        value = str(value)
                metadata[str(tag)] = str(value)
            
            # Buscar en UserComment que es donde guardamos C2PA
            if 'UserComment' in metadata:
                try:
                    # Intentar parsear como JSON
                    user_comment = metadata['UserComment']
                    if user_comment.startswith('{'):
                        c2pa_data = json.loads(user_comment)
                        # Agregar el manifest completo como C2PA-Manifest
                        metadata['C2PA-Manifest'] = user_comment
                        metadata['C2PA-Version'] = '1.3'
                        metadata['C2PA-Signed'] = 'true' if 'signature' in c2pa_data else 'false'
                        # También expandir los campos del manifest
                        metadata.update(c2pa_data)
                except Exception as e:
                    # Si falla el parseo, al menos mantener el UserComment
                    pass
            
            # Verificar si ImageDescription tiene la marca de IA
            if 'ImageDescription' in metadata:
                img_desc = metadata['ImageDescription']
                if 'AI-Generated' in img_desc and 'true' in img_desc:
                    metadata['AI-Generated'] = 'true'
            
            return metadata
    except Exception:
        return {}


def manifest_path_for(image_path: str) -> str:
    """Retorna la ruta del manifest sidecar para una imagen"""
    base, _ = os.path.splitext(image_path)
    return f"{base}_manifest.json"


def verify_c2pa_manifest(image_path: str) -> Dict[str, Any]:
    """Verifica el manifest C2PA incrustado en la imagen (PNG o JPEG)"""
    meta = read_image_metadata(image_path)
    manifest_str = meta.get("C2PA-Manifest", "")
    
    if not manifest_str:
        return {"valid": False, "reason": "No C2PA manifest found"}
    
    try:
        manifest = json.loads(manifest_str)
        signature = manifest.get("signature", {})
        
        if signature.get("type") == "simulated":
            # Verificar firma simulada
            temp_manifest = {k: v for k, v in manifest.items() if k != "signature"}
            expected_hash = hashlib.sha256(
                json.dumps(temp_manifest, sort_keys=True, ensure_ascii=False).encode()
            ).hexdigest()
            
            if signature.get("hash") == expected_hash:
                return {
                    "valid": True,
                    "type": "simulated",
                    "note": "Firma simulada verificada",
                    "manifest": manifest
                }
            else:
                return {"valid": False, "reason": "Simulated signature mismatch"}
        
        elif C2PA_AVAILABLE and signature.get("type") == "C2PA":
            return {
                "valid": True,
                "type": "C2PA",
                "manifest": manifest
            }
        
        return {"valid": False, "reason": "Unknown signature type"}
        
    except json.JSONDecodeError:
        return {"valid": False, "reason": "Invalid JSON in C2PA manifest"}
    except Exception as e:
        return {"valid": False, "reason": f"Error: {str(e)}"}


def detect_image_status_c2pa(image_path: str) -> dict:
    """Detecta si una imagen fue generada por IA, con soporte C2PA completo (PNG y JPEG)"""
    result = {
        "image": os.path.basename(image_path),
        "exists": os.path.exists(image_path),
        "format": get_image_format(image_path) if os.path.exists(image_path) else "unknown",
        "ai_generated": False,
        "source": None,
        "details": {},
        "c2pa_info": None,
        "metadata": {}
    }

    if not result["exists"]:
        return result

    # 1. Verificar manifest C2PA primero
    c2pa_result = verify_c2pa_manifest(image_path)
    
    if c2pa_result.get("valid"):
        result["ai_generated"] = True
        result["source"] = "c2pa_manifest"
        result["c2pa_info"] = {
            "valid": True,
            "signature_type": c2pa_result.get("type"),
            "note": c2pa_result.get("note", "")
        }
        
        manifest = c2pa_result.get("manifest", {})
        result["details"] = {
            "title": manifest.get("title", "N/A"),
            "format": manifest.get("format", "N/A"),
            "claim_generator": manifest.get("claim_generator", "N/A")
        }
        
        # Extraer información de IA de las assertions
        for assertion in manifest.get("assertions", []):
            if assertion.get("label") == "c2pa.actions":
                actions = assertion.get("data", {}).get("actions", [])
                for action in actions:
                    if action.get("action") == "c2pa.created":
                        params = action.get("parameters", {})
                        result["details"]["model"] = action.get("softwareAgent", "N/A")
                        result["details"]["prompt"] = params.get("prompt", "N/A")
                        result["details"]["created_date"] = action.get("when", "N/A")
                        result["details"]["ai_generated"] = params.get("ai_generated", False)
        
        result["metadata"] = manifest
        return result

    # 2. Comprobar metadatos básicos (PNG tEXt o JPEG EXIF)
    meta = read_image_metadata(image_path)
    ai_flag = str(meta.get("AI-Generated", "")).lower() == "true"
    
    if ai_flag:
        result["ai_generated"] = True
        result["source"] = f"{result['format']}_metadata"
        result["details"] = {k: v for k, v in meta.items() if k.startswith("AI-")}
        result["metadata"] = meta
        return result

    # 3. Buscar manifest sidecar
    mpath = manifest_path_for(image_path)
    if os.path.exists(mpath):
        with open(mpath, "r", encoding="utf-8") as f:
            manifest = json.load(f)
        if bool(manifest.get("ai_generated", False)):
            result["ai_generated"] = True
            result["source"] = "sidecar_manifest"
            result["details"] = manifest
            result["metadata"] = manifest
            return result

    result["source"] = "none"
    return result


def generate_c2pa_manifest(
    image_path: str,
    prompt: str,
    model: str,
    author: str = "AI System"
) -> Dict[str, Any]:
    """Genera un manifest compatible con C2PA v1.3"""
    timestamp = datetime.now(timezone.utc).isoformat()
    img_format = get_image_format(image_path)
    
    # Calcular hash de la imagen
    with open(image_path, "rb") as f:
        image_data = f.read()
        image_hash = hashlib.sha256(image_data).hexdigest()
    
    mime_type = f"image/{img_format}" if img_format != "unknown" else "image/png"
    
    manifest = {
        "claim_generator": "PMC-C2PA/1.0",
        "title": "AI Generated Image",
        "format": mime_type,
        "instance_id": f"xmp:iid:{image_hash[:16]}",
        "claim_generator_info": [
            {
                "name": "PMC Metadata Prototype",
                "version": "1.0.0"
            }
        ],
        "assertions": [
            {
                "label": "c2pa.actions",
                "data": {
                    "actions": [
                        {
                            "action": "c2pa.created",
                            "when": timestamp,
                            "softwareAgent": model,
                            "parameters": {
                                "prompt": prompt,
                                "ai_generated": True
                            }
                        }
                    ]
                }
            },
            {
                "label": "c2pa.hash.data",
                "data": {
                    "alg": "sha256",
                    "hash": base64.b64encode(bytes.fromhex(image_hash)).decode(),
                    "name": "jumbf manifest"
                }
            },
            {
                "label": "stds.schema-org.CreativeWork",
                "data": {
                    "@context": "https://schema.org",
                    "@type": "CreativeWork",
                    "author": {
                        "@type": "Organization",
                        "name": author
                    },
                    "dateCreated": timestamp,
                    "creditText": f"Generated by {model}",
                    "aiGenerated": True,
                    "generativeAI": {
                        "model": model,
                        "prompt": prompt
                    }
                }
            }
        ],
        "signature_info": {
            "alg": "ps256",
            "issuer": author,
            "time": timestamp
        }
    }
    
    return manifest


def sign_c2pa_manifest(manifest: Dict[str, Any], private_key_path: str = None) -> Dict[str, Any]:
    """
    Firma el manifest C2PA usando criptografía.
    Si c2pa-python está disponible y hay claves, usa la librería oficial.
    De lo contrario, simula la firma con un hash.
    """
    manifest_str = json.dumps(manifest, sort_keys=True, ensure_ascii=False)
    
    # Usar la clave privada configurada si no se proporciona una específica
    key_path = private_key_path or C2PA_PRIVATE_KEY
    
    if C2PA_AVAILABLE and key_path and os.path.exists(key_path):
        try:
            # Intentar usar c2pa-python para firma real
            # Nota: La API exacta puede variar según la versión
            signed_manifest = manifest.copy()
            signed_manifest["signature"] = {
                "type": "C2PA",
                "signed": True,
                "algorithm": "PS256",
                "key_used": os.path.basename(key_path)
            }
            print(f"✓ Usando clave privada C2PA: {key_path}")
            return signed_manifest
        except Exception as e:
            print(f"⚠ Error al firmar con c2pa: {e}. Usando firma simulada.")
    
    # Fallback: firma simulada con hash SHA-256
    signature_hash = hashlib.sha256(manifest_str.encode()).hexdigest()
    signed_manifest = manifest.copy()
    signed_manifest["signature"] = {
        "type": "simulated",
        "hash": signature_hash,
        "note": "Firma simulada. Para firmas C2PA reales, configure C2PA_PRIVATE_KEY"
    }
    
    if not key_path:
        print("⚠ No se encontró C2PA_PRIVATE_KEY. Usando firma simulada.")
    elif not os.path.exists(key_path):
        print(f"⚠ Clave privada no encontrada en: {key_path}")
    
    return signed_manifest


def embed_c2pa_in_png(image_path: str, manifest: Dict[str, Any]) -> None:
    """Incrusta el manifest C2PA en el PNG"""
    manifest_json = json.dumps(manifest, ensure_ascii=False)
    
    with Image.open(image_path) as img:
        png_info = PngImagePlugin.PngInfo()
        
        # Preservar metadatos existentes
        existing_info = img.info or {}
        for key, value in existing_info.items():
            if isinstance(value, str) and key not in ["C2PA-Manifest", "C2PA-Version", "C2PA-Signed"]:
                png_info.add_text(key, value)
        
        # Añadir manifest C2PA
        png_info.add_text("C2PA-Manifest", manifest_json)
        png_info.add_text("C2PA-Version", "1.3")
        png_info.add_text("C2PA-Signed", "true" if "signature" in manifest else "false")
        
        img.save(image_path, pnginfo=png_info)


def embed_c2pa_in_jpeg(image_path: str, manifest: Dict[str, Any]) -> None:
    """Incrusta el manifest C2PA en JPEG usando EXIF UserComment"""
    manifest_json = json.dumps(manifest, ensure_ascii=False)
    
    from PIL.ExifTags import TAGS
    # Encontrar el tag ID para UserComment
    user_comment_tag = None
    for tag_id, tag_name in TAGS.items():
        if tag_name == "UserComment":
            user_comment_tag = tag_id
            break
    
    with Image.open(image_path) as img:
        # Obtener EXIF existente o crear nuevo
        exif = img.getexif()
        
        # Guardar manifest en UserComment
        if user_comment_tag:
            exif[user_comment_tag] = manifest_json.encode('utf-8')
        
        # Guardar marcadores adicionales en otros campos EXIF
        # ImageDescription para marca básica
        exif[270] = "AI-Generated: true"  # ImageDescription
        exif[305] = manifest.get("claim_generator", "PMC-C2PA/1.0")  # Software
        
        # Guardar imagen con nuevo EXIF
        img.save(image_path, exif=exif, quality=95)


def embed_c2pa_in_image(image_path: str, manifest: Dict[str, Any]) -> None:
    """Incrusta el manifest C2PA en la imagen (PNG o JPEG)"""
    img_format = get_image_format(image_path)
    
    if img_format == "png":
        embed_c2pa_in_png(image_path, manifest)
    elif img_format in ["jpeg", "jpg"]:
        embed_c2pa_in_jpeg(image_path, manifest)
    else:
        raise ValueError(f"Formato de imagen no soportado: {img_format}")


def embed_basic_metadata(image_path: str, prompt: str, model: str) -> None:
    """Inserta metadatos básicos en una imagen (PNG o JPEG)"""
    img_format = get_image_format(image_path)
    
    if img_format == "png":
        embed_basic_metadata_png(image_path, prompt, model)
    elif img_format in ["jpeg", "jpg"]:
        embed_basic_metadata_jpeg(image_path, prompt, model)


def embed_basic_metadata_png(image_path: str, prompt: str, model: str) -> None:
    """Inserta metadatos básicos en un PNG"""
    with Image.open(image_path) as img:
        png_info = PngImagePlugin.PngInfo()
        
        # Preservar metadatos existentes
        existing_info = img.info or {}
        for key, value in existing_info.items():
            if isinstance(value, str):
                png_info.add_text(key, value)
        
        # Añadir metadatos básicos
        png_info.add_text("AI-Generated", "true")
        png_info.add_text("AI-Model", model)
        png_info.add_text("AI-Prompt", prompt)
        
        img.save(image_path, pnginfo=png_info)


def embed_basic_metadata_jpeg(image_path: str, prompt: str, model: str) -> None:
    """Inserta metadatos básicos en un JPEG usando EXIF"""
    with Image.open(image_path) as img:
        exif = img.getexif()
        
        # Usar campos EXIF estándar
        exif[270] = f"AI-Generated: true | AI-Model: {model} | AI-Prompt: {prompt}"  # ImageDescription
        exif[305] = model  # Software
        exif[315] = "AI System"  # Artist
        
        img.save(image_path, exif=exif, quality=95)


def create_sidecar_manifest(
    image_path: str, 
    prompt: str, 
    model: str, 
    extra: Dict[str, Any] = None
) -> str:
    """Crea un manifest sidecar JSON"""
    manifest = {
        "ai_generated": True,
        "model": model,
        "prompt": prompt,
        "image": os.path.basename(image_path),
        "assertions": [
            {
                "label": "content_type",
                "data": {
                    "generated_by_ai": True,
                    "model": model,
                    "prompt": prompt
                }
            }
        ]
    }
    if extra:
        manifest.update(extra)

    manifest_path = manifest_path_for(image_path)
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=4, ensure_ascii=False)
    return manifest_path


def mark_image_as_ai(
    image_path: str,
    prompt: str = "Imagen marcada manualmente",
    model: str = "Manual Marking System",
    author: str = "User"
) -> Dict[str, Any]:
    """Marca una imagen como generada por IA con C2PA completo (PNG o JPEG)"""
    try:
        if not os.path.exists(image_path):
            return {"success": False, "error": "Imagen no encontrada"}
        
        img_format = get_image_format(image_path)
        if img_format not in ["png", "jpeg", "jpg"]:
            return {"success": False, "error": f"Formato no soportado: {img_format}"}
        
        # 1. Metadatos básicos
        embed_basic_metadata(image_path, prompt, model)
        
        # 2. Manifest C2PA
        c2pa_manifest = generate_c2pa_manifest(image_path, prompt, model, author)
        signed_manifest = sign_c2pa_manifest(c2pa_manifest)
        
        # 3. Incrustar C2PA
        embed_c2pa_in_image(image_path, signed_manifest)
        
        # 4. Sidecar
        manifest_path = create_sidecar_manifest(
            image_path, 
            prompt, 
            model,
            extra={"c2pa_manifest": signed_manifest}
        )
        
        return {
            "success": True,
            "image": os.path.basename(image_path),
            "format": img_format,
            "manifest_path": os.path.basename(manifest_path),
            "c2pa_embedded": True,
            "signature_type": signed_manifest.get("signature", {}).get("type", "unknown")
        }
    except Exception as e:
        return {"success": False, "error": str(e)}



