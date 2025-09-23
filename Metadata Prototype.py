import os
import requests
import json

# Configuración
OPENAI_API_KEY = " "
OUTPUT_IMAGE = "output.png"
MANIFEST_FILE = "manifest.json"


def generate_image(prompt: str):
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
    with open(OUTPUT_IMAGE, "wb") as f:
        f.write(img_response.content)

    # guardamos el manifest como AI generated
    manifest = {
        "ai_generated": True,
        "prompt": prompt
    }
    with open(MANIFEST_FILE, "w") as f:
        json.dump(manifest, f, indent=4)

    print(f"Imagen generada en {OUTPUT_IMAGE}")
    print(f"Manifest en {MANIFEST_FILE}")




def create_manifest(prompt: str):
    """
    Crea un archivo JSON manifest con la marca de AI-generated.
    """
    manifest = {
        "assertions": [
            {
                "label": "content_type",
                "data": {
                    "generated_by_ai": True,
                    "model": "OpenAI gpt-image-1",
                    "prompt": prompt
                }
            }
        ]
    }

    with open(MANIFEST_FILE, "w") as f:
        json.dump(manifest, f, indent=4)

    print(f"Manifiesto creado: {MANIFEST_FILE}")


def check_manifest():
    """
    Pide la ruta de la imagen, busca el manifest asociado
    y verifica si está marcada como IA.
    """
    image_path = input("Ingresa la ruta de la imagen: ").strip()

    if not os.path.exists(image_path):
        print(f"La imagen {image_path} no existe.")
        return

    # Construir ruta del manifest asociado
    manifest_path = os.path.splitext(image_path)[0] + "_manifest.json"

    if not os.path.exists(manifest_path):
        print("\nNo existe manifest. La imagen no fue marcada como IA.")
        return

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    ai_generated = manifest.get("ai_generated", False)

    if ai_generated:
        print("\n La imagen está marcada como generada por IA.")
        print("Contenido del manifest:")
        print(json.dumps(manifest, indent=4))
    else:
        print("\nLa imagen no está marcada como IA.")



def menu():
    """
    Menú en consola.
    """
    while True:
        print("\n=== MENÚ PRINCIPAL ===")
        print("1. Generar imagen con IA y marcar como AI-generated")
        print("2. Comprobar si la imagen es IA (leer manifest)")
        print("3. Salir")

        choice = input("Selecciona una opción (1/2/3): ")

        if choice == "1":
            prompt = input("\nEscribe tu prompt para la imagen: ")
            generate_image(prompt)
            create_manifest(prompt)
        elif choice == "2":
            check_manifest()
        elif choice == "3":
            print("Saliendo...")
            break
        else:
            print("Opción inválida, intenta de nuevo.")


if __name__ == "__main__":
    menu()
