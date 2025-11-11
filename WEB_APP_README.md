# 🌐 Aplicación Web - Detección de IA con C2PA

## Descripción

Aplicación web interactiva con Flask que permite marcar y verificar imágenes generadas por IA usando el estándar C2PA v1.3.

## 🚀 Inicio Rápido

### 1. Instalar dependencias
```powershell
pip install -r requirements.txt
```

### 2. Crear imágenes de muestra (opcional)
```powershell
python create_sample_images.py
```

### 3. Iniciar el servidor
```powershell
python web_app.py
```

### 4. Abrir en el navegador
Abre tu navegador en: `http://localhost:5000`

## 📱 Características de la Aplicación

### Pestaña Principal

#### 🏷️ Marcar como IA
Permite subir una imagen PNG y agregarle metadatos C2PA para marcarla como generada por IA.

**Campos disponibles:**
- **Imagen PNG**: Archivo a marcar (obligatorio)
- **Prompt/Descripción**: Texto usado para generar la imagen
- **Modelo**: Nombre del modelo de IA (ej: OpenAI DALL-E 3)
- **Autor**: Nombre del creador u organización

**Proceso:**
1. Selecciona un archivo PNG
2. Rellena los campos opcionales
3. Haz clic en "Marcar como IA con C2PA"
4. La imagen será marcada con:
   - Metadatos PNG básicos
   - Manifest C2PA firmado
   - Archivo sidecar JSON

**Resultado:**
- ✓ Confirmación de marcado exitoso
- Nombre del archivo modificado
- Tipo de firma utilizada
- Ruta del manifest sidecar

#### 🔍 Comprobar si es IA
Verifica si una imagen tiene metadatos C2PA y fue generada por IA.

**Métodos de carga:**
- Arrastrar y soltar archivo PNG
- Seleccionar desde explorador de archivos
- Clic en "Verificar Imagen"

**Proceso de verificación:**
1. Busca manifest C2PA firmado (prioridad)
2. Verifica metadatos PNG básicos
3. Busca manifest sidecar JSON
4. Reporta si es IA o no

**Información mostrada:**
- Estado: IA o No IA
- Origen de la detección
- Modelo utilizado
- Prompt de generación
- Fecha de creación
- Información C2PA:
  - Validez de la firma
  - Tipo de firma (C2PA real o simulada)
  - Notas adicionales

### Pestaña Ejemplos

#### 📸 Imágenes de Muestra

**gato1.png**
- Imagen real sin marca de IA
- Útil para probar detección negativa

**gato2.png**
- Imagen marcada como generada por IA
- Incluye manifest C2PA completo
- Útil para probar detección positiva

**gato3.png**
- Imagen de prueba sin marca
- Para experimentación

**Uso:**
1. Haz clic en el botón "Verificar" de cualquier imagen
2. Los resultados aparecen abajo con:
   - Badge indicando si es IA
   - Origen de la información
   - JSON completo con metadatos

## 🎨 Interfaz de Usuario

### Diseño Responsivo
- Adaptable a móviles, tablets y escritorio
- Grid dinámico que se ajusta al tamaño de pantalla
- Tema oscuro por defecto con soporte para modo claro

### Componentes Visuales

**Badges de Estado:**
- 🟢 Verde: No es IA
- 🔴 Rojo: Generada por IA
- 🟡 Amarillo: Esperando/Sin datos
- 🔵 Azul: Información

**Secciones Expandibles:**
- Detalles de IA
- Información C2PA
- JSON completo (desplegable)

**Animaciones:**
- Transiciones suaves entre pestañas
- Loading spinner durante procesamiento
- Hover effects en tarjetas

## 🛠️ Estructura Técnica

### Backend (Flask)

**Endpoints:**

#### GET /
Página principal con interfaz HTML

#### POST /mark-as-ai
Marca una imagen como generada por IA

**Parámetros:**
- `file`: Archivo PNG (multipart/form-data)
- `prompt`: Descripción opcional
- `model`: Modelo opcional
- `author`: Autor opcional

**Respuesta:**
```json
{
  "success": true,
  "image": "ejemplo.png",
  "manifest_path": "ejemplo_manifest.json",
  "c2pa_embedded": true,
  "signature_type": "simulated"
}
```

#### POST /detect
Detecta si una imagen es generada por IA

**Parámetros:**
- `file`: Archivo PNG subido, O
- `sample`: Nombre de imagen de ejemplo (gato1, gato2, gato3)

**Respuesta:**
```json
{
  "image": "ejemplo.png",
  "exists": true,
  "ai_generated": true,
  "source": "c2pa_manifest",
  "details": {
    "title": "AI Generated Image",
    "model": "OpenAI gpt-image-1",
    "prompt": "un gato en el espacio",
    "created_date": "2025-11-10T10:30:00Z"
  },
  "c2pa_info": {
    "valid": true,
    "signature_type": "simulated",
    "note": "Firma simulada verificada"
  },
  "metadata": { /* Manifest C2PA completo */ }
}
```

### Frontend (JavaScript)

**Funciones principales:**

- `switchTab(tabName)`: Cambia entre pestañas
- `markAsAI(event)`: Marca imagen como IA
- `detectImage()`: Verifica imagen subida
- `detectSample(sample)`: Verifica imagen de ejemplo
- `renderDetectionResult(data, container)`: Muestra resultados de detección
- `setupDropzone()`: Configura drag & drop

## 📁 Archivos Relacionados

```
PMC/
├── web_app.py                  # Servidor Flask
├── detection_utils.py          # Lógica de detección C2PA
├── create_sample_images.py     # Generador de imágenes de muestra
├── templates/
│   └── index.html             # Interfaz web
├── uploads/                   # Carpeta temporal (auto-creada)
├── gato1.png                  # Imagen ejemplo real
├── gato2.png                  # Imagen ejemplo IA
├── gato2_manifest.json        # Manifest de gato2
└── gato3.png                  # Imagen ejemplo prueba
```

## 🔧 Configuración Avanzada

### Variables de Entorno

```powershell
# Clave privada para firmas C2PA reales
$env:C2PA_PRIVATE_KEY = "C:\ruta\a\c2pa_private.pem"

# Certificado C2PA
$env:C2PA_CERTIFICATE = "C:\ruta\a\c2pa_cert.crt"

# API Key de OpenAI (para generar imágenes)
$env:OPENAI_API_KEY = "tu_api_key"
```

### Tamaño Máximo de Archivo
Por defecto: 16MB

Modificar en `web_app.py`:
```python
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 32MB
```

### Puerto y Host
Por defecto: `0.0.0.0:5000`

Modificar en `web_app.py`:
```python
app.run(host="127.0.0.1", port=8080, debug=False)
```

## 🐛 Solución de Problemas

### Error: "No module named 'flask'"
```powershell
pip install Flask
```

### Error: "Address already in use"
El puerto 5000 está ocupado. Opciones:
1. Cambiar el puerto en `web_app.py`
2. Cerrar la aplicación que usa el puerto 5000

### Las imágenes no se muestran
1. Verifica que existen: `gato1.png`, `gato2.png`, `gato3.png`
2. Ejecuta: `python create_sample_images.py`

### Error: "Unable to save file"
Verifica permisos de escritura en la carpeta del proyecto

## 🚀 Despliegue en Producción

### Usando Gunicorn (Linux/Mac)
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 web_app:app
```

### Usando Waitress (Windows)
```powershell
pip install waitress
waitress-serve --host=0.0.0.0 --port=5000 web_app:app
```

### Configuración Nginx (Proxy Reverso)
```nginx
server {
    listen 80;
    server_name tudominio.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 📊 Casos de Uso

### 1. Marcar Contenido Propio
- Fotógrafos marcando imágenes editadas con IA
- Diseñadores indicando uso de herramientas IA
- Verificación de autenticidad de contenido

### 2. Verificación de Contenido
- Periodistas verificando imágenes recibidas
- Moderadores de contenido en plataformas
- Investigadores analizando deepfakes

### 3. Cumplimiento Normativo
- Cumplir regulaciones de transparencia de IA
- Documentar proveniencia del contenido
- Auditorías de contenido digital

### 4. Educación
- Enseñar sobre autenticidad digital
- Demostrar estándares C2PA
- Práctica de detección de IA

## 🔗 Enlaces Útiles

- [Documentación C2PA](https://c2pa.org/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Content Authenticity Initiative](https://contentauthenticity.org/)

## 📝 Licencia

Este proyecto es un prototipo educativo para demostrar el uso de C2PA.

---

**Versión:** 1.0.0  
**Última actualización:** Noviembre 2025
