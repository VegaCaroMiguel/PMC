# Script PowerShell para generar certificados C2PA
# Requiere OpenSSL instalado en el sistema

Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "  Generador de Certificados C2PA" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

# Verificar si OpenSSL está instalado
$opensslPath = (Get-Command openssl -ErrorAction SilentlyContinue).Source
if (-not $opensslPath) {
    Write-Host "ERROR: OpenSSL no está instalado o no está en el PATH" -ForegroundColor Red
    Write-Host ""
    Write-Host "Opciones de instalación:" -ForegroundColor Yellow
    Write-Host "1. Instalar con Chocolatey: choco install openssl" -ForegroundColor White
    Write-Host "2. Descargar desde: https://slproweb.com/products/Win32OpenSSL.html" -ForegroundColor White
    Write-Host "3. Instalar con Git Bash (incluye OpenSSL)" -ForegroundColor White
    exit 1
}

Write-Host "✓ OpenSSL encontrado: $opensslPath" -ForegroundColor Green
Write-Host ""

# Directorio de salida
$certDir = "$PSScriptRoot\certs"
if (-not (Test-Path $certDir)) {
    New-Item -ItemType Directory -Path $certDir | Out-Null
    Write-Host "✓ Directorio creado: $certDir" -ForegroundColor Green
} else {
    Write-Host "✓ Usando directorio: $certDir" -ForegroundColor Green
}

# Archivos de salida
$privateKeyFile = "$certDir\c2pa_private.pem"
$certFile = "$certDir\c2pa_cert.crt"
$publicKeyFile = "$certDir\c2pa_public.pem"

Write-Host ""
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "  Paso 1: Generar clave privada RSA 2048" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

if (Test-Path $privateKeyFile) {
    $overwrite = Read-Host "La clave privada ya existe. ¿Sobrescribir? (s/n)"
    if ($overwrite -ne 's') {
        Write-Host "Operación cancelada" -ForegroundColor Yellow
        exit 0
    }
}

# Generar clave privada
& openssl genrsa -out $privateKeyFile 2048 2>&1 | Out-Null

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Clave privada generada: $privateKeyFile" -ForegroundColor Green
} else {
    Write-Host "ERROR: No se pudo generar la clave privada" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "  Paso 2: Extraer clave pública" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

& openssl rsa -in $privateKeyFile -pubout -out $publicKeyFile 2>&1 | Out-Null

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Clave pública extraída: $publicKeyFile" -ForegroundColor Green
} else {
    Write-Host "ERROR: No se pudo extraer la clave pública" -ForegroundColor Red
}

Write-Host ""
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "  Paso 3: Generar certificado autofirmado" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Por favor, ingresa la información del certificado:" -ForegroundColor Yellow
Write-Host ""

# Información del certificado
$country = Read-Host "País (código de 2 letras, ej: US, ES, MX)"
$state = Read-Host "Estado/Provincia"
$city = Read-Host "Ciudad"
$org = Read-Host "Organización"
$orgUnit = Read-Host "Departamento (opcional)"
$commonName = Read-Host "Nombre común (tu nombre o dominio)"
$email = Read-Host "Email"

# Crear subject para el certificado
$subject = "/C=$country/ST=$state/L=$city/O=$org"
if ($orgUnit) {
    $subject += "/OU=$orgUnit"
}
$subject += "/CN=$commonName/emailAddress=$email"

Write-Host ""
Write-Host "Generando certificado..." -ForegroundColor Yellow

# Generar certificado autofirmado (válido por 1 año)
& openssl req -new -x509 -key $privateKeyFile -out $certFile -days 365 -subj $subject 2>&1 | Out-Null

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Certificado generado: $certFile" -ForegroundColor Green
} else {
    Write-Host "ERROR: No se pudo generar el certificado" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "  Paso 4: Verificar certificado" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

& openssl x509 -in $certFile -text -noout | Select-String -Pattern "Subject:|Issuer:|Not Before|Not After|Public-Key:"

Write-Host ""
Write-Host "=============================================" -ForegroundColor Green
Write-Host "  ✓ CERTIFICADOS GENERADOS EXITOSAMENTE" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Archivos generados:" -ForegroundColor Cyan
Write-Host "  - Clave privada:  $privateKeyFile" -ForegroundColor White
Write-Host "  - Clave pública:  $publicKeyFile" -ForegroundColor White
Write-Host "  - Certificado:    $certFile" -ForegroundColor White
Write-Host ""
Write-Host "⚠ IMPORTANTE: Mantén la clave privada segura y nunca la compartas" -ForegroundColor Yellow
Write-Host ""
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "  Configuración de Variables de Entorno" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Ejecuta los siguientes comandos para configurar el entorno:" -ForegroundColor Yellow
Write-Host ""
Write-Host "`$env:C2PA_PRIVATE_KEY = `"$privateKeyFile`"" -ForegroundColor Green
Write-Host "`$env:C2PA_CERTIFICATE = `"$certFile`"" -ForegroundColor Green
Write-Host ""
Write-Host "O añádelos a tu perfil de PowerShell para hacerlos permanentes:" -ForegroundColor Yellow
Write-Host "notepad `$PROFILE" -ForegroundColor White
Write-Host ""
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "  Siguiente Paso" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Configura las variables de entorno y ejecuta:" -ForegroundColor Yellow
Write-Host "python `"Metadata Prototype.py`"" -ForegroundColor Green
Write-Host ""

# Preguntar si configurar ahora
$configNow = Read-Host "¿Configurar variables de entorno ahora para esta sesión? (s/n)"
if ($configNow -eq 's') {
    $env:C2PA_PRIVATE_KEY = $privateKeyFile
    $env:C2PA_CERTIFICATE = $certFile
    Write-Host ""
    Write-Host "✓ Variables de entorno configuradas para esta sesión" -ForegroundColor Green
    Write-Host ""
    Write-Host "Puedes ejecutar ahora:" -ForegroundColor Yellow
    Write-Host "python `"Metadata Prototype.py`"" -ForegroundColor Green
    Write-Host ""
}

Write-Host "¡Proceso completado!" -ForegroundColor Green
Write-Host ""
