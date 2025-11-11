"""
Script para probar la detección de una imagen marcada
"""
from detection_utils import detect_image_status_c2pa, read_image_metadata
import json
import os

def test_image(image_path):
    """Prueba la detección de una imagen"""
    print("=" * 70)
    print(f"PROBANDO: {image_path}")
    print("=" * 70)
    print()
    
    if not os.path.exists(image_path):
        print(f"❌ Archivo no encontrado: {image_path}")
        return
    
    print("✅ Archivo encontrado")
    print()
    
    # 1. Leer metadatos crudos
    print("📝 METADATOS CRUDOS:")
    print("-" * 70)
    meta = read_image_metadata(image_path)
    for key, value in meta.items():
        if len(str(value)) > 100:
            print(f"{key}: {str(value)[:100]}...")
        else:
            print(f"{key}: {value}")
    print()
    
    # 2. Detección completa
    print("🔍 RESULTADO DE DETECCIÓN:")
    print("-" * 70)
    result = detect_image_status_c2pa(image_path)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print()
    
    # 3. Verificaciones específicas
    print("✓ VERIFICACIONES:")
    print("-" * 70)
    print(f"Formato detectado: {result['format']}")
    print(f"¿Es IA?: {result['ai_generated']}")
    print(f"Fuente: {result['source']}")
    print()
    
    # 4. Buscar campos específicos
    print("🔎 CAMPOS ESPECÍFICOS:")
    print("-" * 70)
    
    # Buscar en metadatos crudos
    if "C2PA-Manifest" in meta:
        print("✅ Tiene C2PA-Manifest en metadatos")
        try:
            manifest = json.loads(meta["C2PA-Manifest"])
            print(f"   Manifest keys: {list(manifest.keys())}")
        except:
            print("   ⚠️ Error al parsear manifest")
    else:
        print("❌ NO tiene C2PA-Manifest en metadatos")
    
    if "AI-Generated" in meta:
        print(f"✅ Tiene AI-Generated: {meta['AI-Generated']}")
    else:
        print("❌ NO tiene AI-Generated")
    
    if "UserComment" in meta:
        print(f"✅ Tiene UserComment (JPEG)")
        uc = meta["UserComment"]
        if len(uc) > 100:
            print(f"   Primeros 100 chars: {uc[:100]}")
        else:
            print(f"   Contenido: {uc}")
    else:
        print("❌ NO tiene UserComment (esperado en JPEG)")
    
    if "ImageDescription" in meta:
        print(f"✅ Tiene ImageDescription: {meta['ImageDescription']}")
    else:
        print("❌ NO tiene ImageDescription")
    
    print()
    print("=" * 70)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        # Buscar mark_gato1.jpg
        possible_paths = [
            "mark_gato1.jpg",
            "uploads/mark_gato1.jpg",
            "output_mark_gato1.jpg"
        ]
        
        image_path = None
        for p in possible_paths:
            if os.path.exists(p):
                image_path = p
                break
        
        if not image_path:
            print("❌ No se encontró mark_gato1.jpg")
            print()
            print("Uso: python test_detection.py <ruta_imagen>")
            print()
            print("O coloca mark_gato1.jpg en la carpeta actual")
            sys.exit(1)
    
    test_image(image_path)
