"""
Script para configurar fácilmente la contraseña/clave C2PA
"""
import os
import sys

def setup_c2pa_key():
    """Asistente para configurar C2PA_PRIVATE_KEY"""
    print("=" * 70)
    print("🔐 ASISTENTE DE CONFIGURACIÓN C2PA")
    print("=" * 70)
    print()
    
    # Verificar si ya está configurada
    current_key = os.getenv("C2PA_PRIVATE_KEY")
    if current_key:
        print(f"ℹ️  Ya tienes una clave configurada (temporalmente):")
        print(f"   {current_key}")
        print()
        resp = input("¿Deseas cambiarla? (s/n): ").lower()
        if resp != 's':
            print("✅ Manteniendo configuración actual.")
            return
    
    print()
    print("📋 Opciones:")
    print()
    print("1️⃣  Generar nueva clave privada (recomendado si no tienes una)")
    print("2️⃣  Usar clave privada existente")
    print("3️⃣  Ver instrucciones de configuración manual")
    print("0️⃣  Salir")
    print()
    
    choice = input("Selecciona una opción (1-3, 0 para salir): ").strip()
    
    if choice == "1":
        generate_new_key()
    elif choice == "2":
        use_existing_key()
    elif choice == "3":
        show_manual_instructions()
    else:
        print("👋 Saliendo...")

def generate_new_key():
    """Genera una nueva clave privada"""
    print()
    print("=" * 70)
    print("🔑 GENERAR NUEVA CLAVE PRIVADA")
    print("=" * 70)
    print()
    
    # Crear carpeta keys si no existe
    keys_dir = os.path.join(os.getcwd(), "keys")
    if not os.path.exists(keys_dir):
        os.makedirs(keys_dir)
        print(f"✅ Carpeta creada: {keys_dir}")
    
    private_key_path = os.path.join(keys_dir, "private_key.pem")
    certificate_path = os.path.join(keys_dir, "certificate.crt")
    
    # Verificar si OpenSSL está disponible
    print("🔍 Verificando OpenSSL...")
    openssl_check = os.system("openssl version > nul 2>&1")
    
    if openssl_check != 0:
        print()
        print("❌ OpenSSL no está instalado o no está en PATH")
        print()
        print("📥 Para instalar OpenSSL en Windows:")
        print("   1. Descarga desde: https://slproweb.com/products/Win32OpenSSL.html")
        print("   2. Instala 'Win64 OpenSSL v3.x.x Light'")
        print("   3. Durante instalación, selecciona 'Add to System PATH'")
        print()
        print("🔄 Alternativa: Usa Git Bash (viene con OpenSSL)")
        print("   - Abre Git Bash y ejecuta este script allí")
        print()
        input("Presiona ENTER para continuar...")
        return
    
    print("✅ OpenSSL disponible")
    print()
    
    # Generar clave privada
    print("🔐 Generando clave privada RSA 2048 bits...")
    cmd_key = f'openssl genrsa -out "{private_key_path}" 2048'
    result = os.system(cmd_key)
    
    if result == 0:
        print(f"✅ Clave privada generada: {private_key_path}")
    else:
        print("❌ Error al generar clave privada")
        return
    
    print()
    
    # Generar certificado autofirmado
    print("📜 Generando certificado autofirmado...")
    print()
    print("⚠️  OpenSSL te pedirá información:")
    print("   - Country Name: ES (o tu país)")
    print("   - State/Province: (puedes dejarlo en blanco)")
    print("   - City: (puedes dejarlo en blanco)")
    print("   - Organization Name: Tu nombre u organización")
    print("   - Common Name: Tu nombre")
    print("   - Email: (puedes dejarlo en blanco)")
    print()
    input("Presiona ENTER para continuar...")
    print()
    
    cmd_cert = f'openssl req -new -x509 -key "{private_key_path}" -out "{certificate_path}" -days 365'
    result = os.system(cmd_cert)
    
    if result == 0:
        print()
        print(f"✅ Certificado generado: {certificate_path}")
    else:
        print("❌ Error al generar certificado")
    
    print()
    print("=" * 70)
    print("✅ CLAVES GENERADAS EXITOSAMENTE")
    print("=" * 70)
    print()
    print(f"📂 Ubicación de tus claves:")
    print(f"   Clave privada: {private_key_path}")
    print(f"   Certificado:   {certificate_path}")
    print()
    
    # Configurar variable de entorno
    configure_environment_variable(private_key_path, certificate_path)
    
    # Crear .gitignore
    gitignore_path = os.path.join(keys_dir, ".gitignore")
    with open(gitignore_path, 'w') as f:
        f.write("*.pem\n*.key\n*.crt\n")
    print(f"✅ Archivo .gitignore creado en carpeta keys")
    print()

def use_existing_key():
    """Usar una clave privada existente"""
    print()
    print("=" * 70)
    print("📁 USAR CLAVE PRIVADA EXISTENTE")
    print("=" * 70)
    print()
    
    print("Por favor, ingresa la ruta COMPLETA a tu archivo de clave privada (.pem o .key)")
    print("Ejemplo: C:\\Users\\danie\\PMC\\keys\\private_key.pem")
    print()
    
    key_path = input("Ruta de la clave privada: ").strip().strip('"')
    
    if not key_path:
        print("❌ No se ingresó ninguna ruta")
        return
    
    if not os.path.exists(key_path):
        print(f"❌ Archivo no encontrado: {key_path}")
        return
    
    # Verificar que es un archivo PEM válido
    try:
        with open(key_path, 'r') as f:
            first_line = f.readline().strip()
            if "BEGIN" not in first_line or "PRIVATE KEY" not in first_line:
                print("⚠️  Advertencia: El archivo no parece ser una clave privada PEM válida")
                resp = input("¿Continuar de todos modos? (s/n): ").lower()
                if resp != 's':
                    return
    except Exception as e:
        print(f"❌ Error al leer archivo: {e}")
        return
    
    print()
    print(f"✅ Clave privada encontrada: {key_path}")
    print()
    
    # Preguntar por certificado (opcional)
    cert_path = None
    resp = input("¿Tienes un certificado (.crt)? (s/n): ").lower()
    if resp == 's':
        cert_path = input("Ruta del certificado: ").strip().strip('"')
        if cert_path and not os.path.exists(cert_path):
            print(f"⚠️  Certificado no encontrado: {cert_path}")
            cert_path = None
    
    # Configurar variable de entorno
    configure_environment_variable(key_path, cert_path)

def configure_environment_variable(key_path, cert_path=None):
    """Configura la variable de entorno"""
    print()
    print("=" * 70)
    print("⚙️  CONFIGURAR VARIABLE DE ENTORNO")
    print("=" * 70)
    print()
    
    print("🔧 Comandos para configurar (elige uno):")
    print()
    print("📘 PowerShell (sesión actual):")
    print(f'   $env:C2PA_PRIVATE_KEY="{key_path}"')
    if cert_path:
        print(f'   $env:C2PA_CERTIFICATE="{cert_path}"')
    print()
    
    print("📗 CMD (sesión actual):")
    print(f'   set C2PA_PRIVATE_KEY={key_path}')
    if cert_path:
        print(f'   set C2PA_CERTIFICATE={cert_path}')
    print()
    
    print("📕 PowerShell (configuración PERMANENTE):")
    print(f'   [System.Environment]::SetEnvironmentVariable("C2PA_PRIVATE_KEY", "{key_path}", "User")')
    if cert_path:
        print(f'   [System.Environment]::SetEnvironmentVariable("C2PA_CERTIFICATE", "{cert_path}", "User")')
    print()
    
    print("💡 RECOMENDACIÓN:")
    print("   1. Copia el comando de PowerShell (sesión actual)")
    print("   2. Pégalo en tu terminal de PowerShell")
    print("   3. Reinicia VS Code para que tome la variable")
    print()
    
    resp = input("¿Quieres que intente configurarlo automáticamente? (s/n): ").lower()
    
    if resp == 's':
        try:
            # Configurar para usuario actual (permanente)
            os.system(f'setx C2PA_PRIVATE_KEY "{key_path}"')
            if cert_path:
                os.system(f'setx C2PA_CERTIFICATE "{cert_path}"')
            
            print()
            print("✅ Variable de entorno configurada PERMANENTEMENTE")
            print()
            print("⚠️  IMPORTANTE: Debes REINICIAR VS Code o tu terminal para que tome efecto")
            print()
        except Exception as e:
            print(f"❌ Error al configurar: {e}")
            print("Por favor, configúralo manualmente con los comandos de arriba")
    else:
        print()
        print("👍 Configúralo manualmente con los comandos de arriba")
    
    print()

def show_manual_instructions():
    """Muestra instrucciones manuales"""
    print()
    print("=" * 70)
    print("📖 INSTRUCCIONES DE CONFIGURACIÓN MANUAL")
    print("=" * 70)
    print()
    
    print("1️⃣  Si NO tienes clave privada:")
    print()
    print("   a) Instala OpenSSL (si no lo tienes):")
    print("      - Windows: https://slproweb.com/products/Win32OpenSSL.html")
    print("      - O usa Git Bash que incluye OpenSSL")
    print()
    print("   b) Genera tu clave privada:")
    print("      openssl genrsa -out private_key.pem 2048")
    print()
    print("   c) Genera certificado autofirmado:")
    print("      openssl req -new -x509 -key private_key.pem -out certificate.crt -days 365")
    print()
    
    print("2️⃣  Configura la variable de entorno:")
    print()
    print("   PowerShell (temporal):")
    print('   $env:C2PA_PRIVATE_KEY="C:\\ruta\\completa\\a\\private_key.pem"')
    print()
    print("   PowerShell (permanente):")
    print('   [System.Environment]::SetEnvironmentVariable("C2PA_PRIVATE_KEY", "C:\\ruta\\completa\\a\\private_key.pem", "User")')
    print()
    
    print("3️⃣  Reinicia VS Code o tu terminal")
    print()
    
    print("4️⃣  Verifica la configuración:")
    print("   python check_c2pa_config.py")
    print()
    
    input("Presiona ENTER para continuar...")

if __name__ == "__main__":
    try:
        setup_c2pa_key()
        print()
        print("✅ Proceso completado")
        print()
    except KeyboardInterrupt:
        print()
        print("👋 Proceso cancelado por el usuario")
    except Exception as e:
        print()
        print(f"❌ Error: {e}")
    finally:
        input("Presiona ENTER para salir...")
