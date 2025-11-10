# Configuración C2PA

## Instalación de Dependencias

```powershell
pip install -r requirements.txt
```

## Generación de Claves para Firmas C2PA

### Opción 1: Firma Simulada (Por defecto)
El sistema funciona automáticamente con firmas simuladas usando hash SHA-256. No requiere configuración adicional.

### Opción 2: Firmas C2PA Reales

Para generar firmas C2PA válidas necesitas:

#### 1. Generar una clave privada RSA

```powershell
# Usando OpenSSL (si está instalado)
openssl genrsa -out c2pa_private.pem 2048
```

#### 2. Generar un certificado autofirmado

```powershell
openssl req -new -x509 -key c2pa_private.pem -out c2pa_cert.crt -days 365
```

Durante este proceso se te pedirá información:
- Country Name (código de 2 letras): US
- State: Tu estado
- Locality: Tu ciudad
- Organization Name: Nombre de tu organización
- Organizational Unit: Tu departamento
- Common Name: Tu nombre o dominio
- Email Address: Tu email

#### 3. Configurar variables de entorno

```powershell
# Windows PowerShell
$env:C2PA_PRIVATE_KEY = "c:\Users\danie\PMC\c2pa_private.pem"
$env:C2PA_CERTIFICATE = "c:\Users\danie\PMC\c2pa_cert.crt"
```

Para hacerlo permanente, añade estas variables a tu perfil de PowerShell o configúralas en las variables de entorno del sistema.

#### 4. Ejecutar el programa

```powershell
python "Metadata Prototype.py"
```

## Estructura del Manifest C2PA

El sistema genera manifests compatibles con C2PA v1.3 que incluyen:

### 1. Información del Claim
- `claim_generator`: Identificador del sistema que crea el manifest
- `title`: Título del contenido
- `format`: Tipo MIME del archivo
- `instance_id`: Identificador único basado en hash

### 2. Assertions (Afirmaciones)

#### a) c2pa.actions
Registra las acciones realizadas sobre el contenido:
- Acción: `c2pa.created` (creación)
- Timestamp en formato ISO 8601
- Software agent (modelo de IA)
- Parámetros: prompt, ai_generated flag

#### b) c2pa.hash.data
Hash criptográfico del contenido:
- Algoritmo: SHA-256
- Hash en Base64
- Nombre del recurso

#### c) stds.schema-org.CreativeWork
Metadatos estructurados usando Schema.org:
- Información del autor
- Fecha de creación
- Texto de crédito
- Flag de generación por IA
- Datos del modelo generativo

### 3. Información de Firma
- Algoritmo: PS256 (RSASSA-PSS con SHA-256)
- Emisor
- Timestamp de firma

## Verificación de Manifests

El sistema verifica automáticamente:

1. **Presencia del manifest C2PA** en los metadatos PNG
2. **Validez de la firma** (simulada o real según configuración)
3. **Integridad del hash** del contenido
4. **Estructura del manifest** según estándar C2PA

### Tipos de Verificación

#### Firma Simulada
- Verifica que el hash SHA-256 del manifest coincida
- Rápido y sin requisitos de infraestructura PKI
- Adecuado para desarrollo y pruebas

#### Firma C2PA Real
- Verifica la firma criptográfica RSA
- Valida la cadena de certificados
- Compatible con herramientas C2PA estándar
- Requerido para producción

## Compatibilidad

### Formatos Soportados
- ✅ PNG (usando chunks tEXt/iTXt)
- 🚧 JPEG (futuro: usando segmentos JUMBF)
- 🚧 WebP (futuro)

### Herramientas Compatibles
- **c2pa-python**: Librería oficial de Python
- **c2patool**: Herramienta de línea de comandos
- **Adobe Content Credentials**: Visor web
- **Verify**: Aplicación de verificación

## Limitaciones Actuales

1. **PNG únicamente**: JPEG requiere soporte JUMBF nativo
2. **Chunks tEXt**: Aproximación a JUMBF, no es el estándar oficial para PNG
3. **Certificados**: Los certificados autofirmados no son confiables en producción
4. **c2pa-python**: La API está en desarrollo y puede cambiar

## Mejores Prácticas

### Para Desarrollo
```powershell
# Usar firma simulada (por defecto)
python "Metadata Prototype.py"
```

### Para Producción
1. Obtener certificados de una CA confiable
2. Configurar variables de entorno con rutas seguras
3. Usar almacenamiento seguro para claves privadas
4. Implementar rotación de certificados
5. Mantener logs de auditoría

## Solución de Problemas

### Error: "c2pa module not found"
```powershell
pip install c2pa-python
```

### Error: "Invalid private key"
Verifica que:
1. El archivo .pem existe en la ruta especificada
2. Tiene permisos de lectura
3. Es una clave RSA válida de al menos 2048 bits

### La firma no se verifica
1. Comprueba que la imagen no ha sido modificada
2. Verifica que los metadatos no se perdieron al guardar
3. Confirma que usas la misma clave para firmar y verificar

## Referencias

- [C2PA Specification](https://c2pa.org/specifications/specifications/1.3/specs/C2PA_Specification.html)
- [c2pa-python GitHub](https://github.com/contentauth/c2pa-python)
- [Content Authenticity Initiative](https://contentauthenticity.org/)
- [Coalition for Content Provenance and Authenticity](https://c2pa.org/)
