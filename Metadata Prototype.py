import os
import requests
import json
from typing import Dict, Any
from PIL import Image, PngImagePlugin

# Configuración
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", " ")
OUTPUT_IMAGE = "output.png"


def _embed_png_metadata(image_path: str, metadata: Dict[str, str]) -> None:
    """
    Inserta metadatos tEXt/iTXt en un PNG utilizando Pillow.
    """
    with Image.open(image_path) as img:
        png_info = PngImagePlugin.PngInfo()
        # Preservar metadatos existentes si los hay
        existing_info = img.info or {}
        for key, value in existing_info.items():
            # Solo copiar claves de texto simples
            if isinstance(value, str):
                png_info.add_text(key, value)

        for key, value in metadata.items():
            png_info.add_text(key, value)

        img.save(image_path, pnginfo=png_info)


def _read_png_metadata(image_path: str) -> Dict[str, Any]:
    """
    Lee metadatos tEXt/iTXt de un PNG. Devuelve un dict plano.
    """
    try:
        with Image.open(image_path) as img:
            info = img.info or {}
            return {str(k): (str(v) if not isinstance(v, str) else v) for k, v in info.items()}
    except Exception:
        return {}


def _manifest_path_for(image_path: str) -> str:
    base, _ = os.path.splitext(image_path)
    return f"{base}_manifest.json"


def _create_sidecar_manifest(image_path: str, prompt: str, model: str, extra: Dict[str, Any] | None = None) -> str:
    manifest: Dict[str, Any] = {
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

    manifest_path = _manifest_path_for(image_path)
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=4, ensure_ascii=False)
    return manifest_path


def generate_image(prompt: str) -> str:
    url = "https://api.openai.com/v1/images/generations"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "gpt-image-1",
        "prompt": prompt if prompt.strip() else "imagen de prueba generada con IA",
        "size": "auto"
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code != 200:
        print("Error en la API:", response.text)
        response.raise_for_status()

    data = response.json()

    # la API devuelve una URL de la imagen
    image_url = data["data"][0]["url"]

    # descargamos la imagen desde esa URL
    img_response = requests.get(image_url)
    image_path = OUTPUT_IMAGE
    with open(image_path, "wb") as f:
        f.write(img_response.content)

    # Insertar marca en metadatos PNG
    model_name = "OpenAI gpt-image-1"
    _embed_png_metadata(
        image_path,
        {
            "AI-Generated": "true",
            "AI-Model": model_name,
            "AI-Prompt": prompt,
            "C2PA-Placeholder": "true"  # Indicador para posible adopción C2PA
        },
    )

    # Crear manifest sidecar por imagen
    manifest_path = _create_sidecar_manifest(image_path, prompt, model_name)

    print(f"Imagen generada en {image_path}")
    print(f"Manifest en {manifest_path}")
    return image_path

def mark_existing_image():
    """
    Marca un PNG existente como generado por IA: inserta metadatos y crea sidecar.
    """
    image_path = input("Ingresa la ruta del PNG a marcar: ").strip()
    if not os.path.exists(image_path):
        print(f"La imagen {image_path} no existe.")
        return
    prompt = input("Prompt o descripción (opcional): ").strip()
    model_name = input("Modelo (ej. OpenAI gpt-image-1) [opcional]: ").strip() or "unknown"

    _embed_png_metadata(
        image_path,
        {
            "AI-Generated": "true",
            "AI-Model": model_name,
            "AI-Prompt": prompt,
            "C2PA-Placeholder": "true",
        },
    )
    manifest_path = _create_sidecar_manifest(image_path, prompt, model_name)
    print("\nMarcado completado.")
    print(f"Manifest en {manifest_path}")


def check_manifest():
    """
    Pide la ruta de la imagen, busca el manifest asociado
    y verifica si está marcada como IA.
    """
    image_path = input("Ingresa la ruta de la imagen: ").strip()

    if not os.path.exists(image_path):
        print(f"La imagen {image_path} no existe.")
        return

    # 1) Comprobar metadatos embebidos primero
    meta = _read_png_metadata(image_path)
    ai_flag = str(meta.get("AI-Generated", "")).lower() == "true"

    if ai_flag:
        print("\nLa imagen está marcada como generada por IA (metadatos PNG).")
        print("Metadatos relevantes:")
        subset = {k: v for k, v in meta.items() if k.startswith("AI-") or k == "C2PA-Placeholder"}
        print(json.dumps(subset, indent=4, ensure_ascii=False))
        return

    # 2) Fallback: buscar manifest sidecar
    manifest_path = _manifest_path_for(image_path)
    if os.path.exists(manifest_path):
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
        ai_generated = bool(manifest.get("ai_generated", False))
        if ai_generated:
            print("\nLa imagen está marcada como generada por IA (sidecar manifest).")
            print("Contenido del manifest:")
            print(json.dumps(manifest, indent=4, ensure_ascii=False))
            return

    print("\nNo se encontró marca de IA en metadatos ni manifest sidecar.")



def menu():
    """
    Menú en consola.
    """
    while True:
        print("\n=== MENÚ PRINCIPAL ===")
        print("1. Generar imagen con IA y marcar (metadatos + manifest)")
        print("2. Comprobar si la imagen es IA (metadatos PNG y manifest sidecar)")
        print("3. Marcar un PNG existente como IA")
        print("4. Salir")

        choice = input("Selecciona una opción (1/2/3/4): ")

        if choice == "1":
            prompt = input("\nEscribe tu prompt para la imagen: ")
            generate_image(prompt)
        elif choice == "2":
            check_manifest()
        elif choice == "3":
            mark_existing_image()
        elif choice == "4":
            print("Saliendo...")
            break
        else:
            print("Opción inválida, intenta de nuevo.")


if __name__ == "__main__":
    menu()
