"""
Script para verificar la configuración de C2PA
Comprueba que las claves privadas estén configuradas correctamente
"""
import os
import sys

def check_c2pa_configuration():
    """Verifica la configuración de C2PA"""
    print("=" * 60)
    print("🔍 VERIFICACIÓN DE CONFIGURACIÓN C2PA")
    print("=" * 60)
    print()
    
    # Verificar variable de entorno C2PA_PRIVATE_KEY
    private_key = os.getenv("C2PA_PRIVATE_KEY", None)
    certificate = os.getenv("C2PA_CERTIFICATE", None)
    
    print("1️⃣ Variables de Entorno:")
    print("-" * 60)
    
    if private_key:
        print(f"✅ C2PA_PRIVATE_KEY configurada: {private_key}")
        
        # Verificar si el archivo existe
        if os.path.exists(private_key):
            print(f"   ✅ Archivo encontrado")
            
            # Verificar permisos de lectura
            if os.access(private_key, os.R_OK):
                print(f"   ✅ Archivo legible")
                
                # Mostrar tamaño del archivo
                size = os.path.getsize(private_key)
                print(f"   📊 Tamaño: {size} bytes")
                
                # Verificar que es un archivo .pem o .key
                ext = os.path.splitext(private_key)[1].lower()
                if ext in ['.pem', '.key']:
                    print(f"   ✅ Extensión válida: {ext}")
                else:
                    print(f"   ⚠️  Extensión inusual: {ext} (esperado .pem o .key)")
                
                # Intentar leer las primeras líneas
                try:
                    with open(private_key, 'r') as f:
                        first_line = f.readline().strip()
                        if "BEGIN" in first_line and "PRIVATE KEY" in first_line:
                            print(f"   ✅ Formato de clave privada detectado")
                        else:
                            print(f"   ⚠️  Primera línea no parece clave PEM: {first_line[:50]}")
                except Exception as e:
                    print(f"   ⚠️  Error al leer archivo: {e}")
            else:
                print(f"   ❌ Archivo NO legible (verificar permisos)")
        else:
            print(f"   ❌ Archivo NO encontrado en esa ruta")
    else:
        print(f"❌ C2PA_PRIVATE_KEY NO configurada")
        print(f"   💡 Para configurarla:")
        print(f"      Windows PowerShell: $env:C2PA_PRIVATE_KEY='ruta\\a\\tu\\clave.pem'")
        print(f"      Windows CMD: set C2PA_PRIVATE_KEY=ruta\\a\\tu\\clave.pem")
        print(f"      Linux/Mac: export C2PA_PRIVATE_KEY='ruta/a/tu/clave.pem'")
    
    print()
    
    if certificate:
        print(f"✅ C2PA_CERTIFICATE configurada: {certificate}")
        if os.path.exists(certificate):
            print(f"   ✅ Certificado encontrado")
        else:
            print(f"   ❌ Certificado NO encontrado")
    else:
        print(f"⚠️  C2PA_CERTIFICATE NO configurada (opcional)")
    
    print()
    print("2️⃣ Librería c2pa-python:")
    print("-" * 60)
    
    try:
        import c2pa
        print(f"✅ c2pa-python instalada")
        try:
            version = c2pa.__version__
            print(f"   📦 Versión: {version}")
        except:
            print(f"   📦 Versión: No disponible")
    except ImportError:
        print(f"❌ c2pa-python NO instalada")
        print(f"   💡 Para instalar: pip install c2pa-python")
    
    print()
    print("3️⃣ Archivos del Proyecto:")
    print("-" * 60)
    
    # Verificar que los archivos principales usan C2PA_PRIVATE_KEY
    files_to_check = [
        "detection_utils.py",
        "Metadata Prototype.py",
        "web_app.py"
    ]
    
    for filename in files_to_check:
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
                if "C2PA_PRIVATE_KEY" in content:
                    print(f"✅ {filename} - Usa C2PA_PRIVATE_KEY")
                else:
                    print(f"⚠️  {filename} - NO usa C2PA_PRIVATE_KEY")
        else:
            print(f"❌ {filename} - Archivo no encontrado")
    
    print()
    print("=" * 60)
    print("4️⃣ RESUMEN:")
    print("=" * 60)
    
    if private_key and os.path.exists(private_key):
        print("✅ Tu configuración C2PA está CORRECTA")
        print("✅ Las imágenes marcadas usarán tu clave privada")
        print()
        print("🔒 Tipo de firma que se usará: C2PA con clave privada")
    elif private_key and not os.path.exists(private_key):
        print("⚠️  Configuración INCOMPLETA:")
        print("   - Variable configurada pero archivo no encontrado")
        print("   - Verifica la ruta de tu clave privada")
        print()
        print("🔓 Tipo de firma que se usará: Simulada (no criptográfica)")
    else:
        print("⚠️  Configuración FALTANTE:")
        print("   - Variable de entorno C2PA_PRIVATE_KEY no configurada")
        print("   - Las firmas serán simuladas (solo hash SHA-256)")
        print()
        print("🔓 Tipo de firma que se usará: Simulada (no criptográfica)")
    
    print("=" * 60)
    print()


if __name__ == "__main__":
    check_c2pa_configuration()
    input("\nPresiona ENTER para salir...")
