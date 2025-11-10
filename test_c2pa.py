"""
Script de pruebas para verificar la funcionalidad C2PA
"""

import os
import sys
import json
from pathlib import Path

# Importar funciones del módulo principal
try:
    from PIL import Image, PngImagePlugin
    import_success = True
except ImportError as e:
    print(f"❌ Error al importar dependencias: {e}")
    print("Por favor ejecuta: pip install -r requirements.txt")
    import_success = False
    sys.exit(1)

# Importar el módulo principal
try:
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "metadata_prototype", 
        "Metadata Prototype.py"
    )
    mp = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mp)
except Exception as e:
    print(f"❌ Error al importar Metadata Prototype.py: {e}")
    sys.exit(1)


def print_header(text):
    """Imprime un encabezado formateado"""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")


def test_c2pa_availability():
    """Prueba 1: Verificar disponibilidad de C2PA"""
    print_header("TEST 1: Verificar disponibilidad de C2PA")
    
    if mp.C2PA_AVAILABLE:
        print("✓ c2pa-python está instalado")
    else:
        print("⚠ c2pa-python NO está instalado (usando firma simulada)")
    
    if mp.C2PA_PRIVATE_KEY and os.path.exists(mp.C2PA_PRIVATE_KEY):
        print(f"✓ Clave privada configurada: {mp.C2PA_PRIVATE_KEY}")
    else:
        print("⚠ Clave privada no configurada (usando firma simulada)")
    
    if mp.C2PA_CERTIFICATE and os.path.exists(mp.C2PA_CERTIFICATE):
        print(f"✓ Certificado configurado: {mp.C2PA_CERTIFICATE}")
    else:
        print("⚠ Certificado no configurado")
    
    return True


def test_create_test_image():
    """Prueba 2: Crear imagen de prueba"""
    print_header("TEST 2: Crear imagen de prueba PNG")
    
    test_image = "test_c2pa.png"
    
    # Crear una imagen simple de prueba
    img = Image.new('RGB', (400, 300), color='#3498db')
    img.save(test_image)
    
    if os.path.exists(test_image):
        print(f"✓ Imagen de prueba creada: {test_image}")
        return test_image
    else:
        print("❌ No se pudo crear la imagen de prueba")
        return None


def test_generate_c2pa_manifest(image_path):
    """Prueba 3: Generar manifest C2PA"""
    print_header("TEST 3: Generar manifest C2PA")
    
    try:
        manifest = mp._generate_c2pa_manifest(
            image_path=image_path,
            prompt="Imagen de prueba generada con IA",
            model="Test Model v1.0",
            author="Test System"
        )
        
        print("✓ Manifest C2PA generado exitosamente")
        print("\n📋 Contenido del manifest:")
        print(json.dumps(manifest, indent=2, ensure_ascii=False)[:500] + "...")
        
        # Verificar estructura
        required_keys = ["claim_generator", "assertions", "signature_info"]
        for key in required_keys:
            if key in manifest:
                print(f"  ✓ Contiene '{key}'")
            else:
                print(f"  ❌ Falta '{key}'")
                return None
        
        return manifest
    except Exception as e:
        print(f"❌ Error al generar manifest: {e}")
        return None


def test_sign_manifest(manifest):
    """Prueba 4: Firmar manifest"""
    print_header("TEST 4: Firmar manifest C2PA")
    
    try:
        signed_manifest = mp._sign_c2pa_manifest(manifest, mp.C2PA_PRIVATE_KEY)
        
        if "signature" in signed_manifest:
            sig_type = signed_manifest["signature"].get("type", "unknown")
            print(f"✓ Manifest firmado exitosamente")
            print(f"  Tipo de firma: {sig_type}")
            
            if sig_type == "simulated":
                print(f"  Hash: {signed_manifest['signature'].get('hash', 'N/A')[:16]}...")
            
            return signed_manifest
        else:
            print("❌ Firma no encontrada en el manifest")
            return None
    except Exception as e:
        print(f"❌ Error al firmar manifest: {e}")
        return None


def test_embed_c2pa(image_path, signed_manifest):
    """Prueba 5: Incrustar manifest en PNG"""
    print_header("TEST 5: Incrustar manifest C2PA en PNG")
    
    try:
        mp._embed_c2pa_in_png(image_path, signed_manifest)
        
        # Verificar que se incrustó
        meta = mp._read_png_metadata(image_path)
        
        if "C2PA-Manifest" in meta:
            print("✓ Manifest C2PA incrustado en metadatos PNG")
            print(f"  Tamaño del manifest: {len(meta['C2PA-Manifest'])} caracteres")
            
            if "C2PA-Version" in meta:
                print(f"  Versión C2PA: {meta['C2PA-Version']}")
            
            if "C2PA-Signed" in meta:
                print(f"  Firmado: {meta['C2PA-Signed']}")
            
            return True
        else:
            print("❌ Manifest no encontrado en metadatos PNG")
            return False
    except Exception as e:
        print(f"❌ Error al incrustar manifest: {e}")
        return False


def test_verify_c2pa(image_path):
    """Prueba 6: Verificar manifest C2PA"""
    print_header("TEST 6: Verificar manifest C2PA")
    
    try:
        result = mp._verify_c2pa_manifest(image_path)
        
        if result.get("valid"):
            print("✓ Manifest C2PA VÁLIDO")
            print(f"  Tipo: {result.get('type', 'unknown')}")
            
            if result.get("note"):
                print(f"  Nota: {result.get('note')}")
            
            manifest = result.get("manifest", {})
            if manifest:
                print(f"  Título: {manifest.get('title', 'N/A')}")
                print(f"  Generador: {manifest.get('claim_generator', 'N/A')}")
            
            return True
        else:
            print(f"❌ Manifest NO VÁLIDO")
            print(f"  Razón: {result.get('reason', 'desconocida')}")
            return False
    except Exception as e:
        print(f"❌ Error al verificar manifest: {e}")
        return False


def test_sidecar_creation(image_path):
    """Prueba 7: Crear manifest sidecar"""
    print_header("TEST 7: Crear manifest sidecar")
    
    try:
        manifest_path = mp._create_sidecar_manifest(
            image_path=image_path,
            prompt="Imagen de prueba",
            model="Test Model v1.0",
            extra={"test": True}
        )
        
        if os.path.exists(manifest_path):
            print(f"✓ Manifest sidecar creado: {manifest_path}")
            
            with open(manifest_path, 'r', encoding='utf-8') as f:
                sidecar = json.load(f)
            
            print(f"  AI Generated: {sidecar.get('ai_generated', False)}")
            print(f"  Model: {sidecar.get('model', 'N/A')}")
            print(f"  Assertions: {len(sidecar.get('assertions', []))}")
            
            return manifest_path
        else:
            print("❌ Manifest sidecar no creado")
            return None
    except Exception as e:
        print(f"❌ Error al crear sidecar: {e}")
        return None


def run_all_tests():
    """Ejecuta todas las pruebas"""
    print("\n" + "="*60)
    print("  SUITE DE PRUEBAS C2PA")
    print("  Metadata Prototype - Verificación de Funcionalidad")
    print("="*60)
    
    results = []
    
    # Test 1: Disponibilidad
    results.append(("Disponibilidad C2PA", test_c2pa_availability()))
    
    # Test 2: Crear imagen
    image_path = test_create_test_image()
    results.append(("Crear imagen de prueba", image_path is not None))
    
    if not image_path:
        print("\n❌ No se puede continuar sin imagen de prueba")
        return
    
    # Test 3: Generar manifest
    manifest = test_generate_c2pa_manifest(image_path)
    results.append(("Generar manifest C2PA", manifest is not None))
    
    if not manifest:
        print("\n❌ No se puede continuar sin manifest")
        return
    
    # Test 4: Firmar manifest
    signed_manifest = test_sign_manifest(manifest)
    results.append(("Firmar manifest", signed_manifest is not None))
    
    if not signed_manifest:
        print("\n❌ No se puede continuar sin firma")
        return
    
    # Test 5: Incrustar en PNG
    embed_success = test_embed_c2pa(image_path, signed_manifest)
    results.append(("Incrustar manifest en PNG", embed_success))
    
    # Test 6: Verificar
    verify_success = test_verify_c2pa(image_path)
    results.append(("Verificar manifest C2PA", verify_success))
    
    # Test 7: Sidecar
    sidecar_path = test_sidecar_creation(image_path)
    results.append(("Crear manifest sidecar", sidecar_path is not None))
    
    # Resumen
    print_header("RESUMEN DE PRUEBAS")
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✓ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if success:
            passed += 1
    
    print(f"\n{'='*60}")
    print(f"  Resultado: {passed}/{total} pruebas exitosas")
    print(f"{'='*60}\n")
    
    if passed == total:
        print("🎉 ¡Todas las pruebas pasaron exitosamente!")
    else:
        print("⚠ Algunas pruebas fallaron. Revisa los errores arriba.")
    
    # Limpiar archivos de prueba
    cleanup = input("\n¿Eliminar archivos de prueba? (s/n): ")
    if cleanup.lower() == 's':
        if os.path.exists(image_path):
            os.remove(image_path)
            print(f"✓ Eliminado: {image_path}")
        
        if sidecar_path and os.path.exists(sidecar_path):
            os.remove(sidecar_path)
            print(f"✓ Eliminado: {sidecar_path}")
    
    print("\n✓ Pruebas completadas\n")


if __name__ == "__main__":
    if not import_success:
        sys.exit(1)
    
    run_all_tests()
