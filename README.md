# 🧮 Sistema de Finanzas Personales - Deducciones SRI Ecuador

Sistema completo para gestionar deducciones del SRI (Servicio de Rentas Internas) de Ecuador con interfaz moderna, procesamiento automático de facturas con OCR y análisis inteligente.

![Dashboard Preview](static/images/dashboard-preview.png)

## 🌟 Características Principales

### 📊 Dashboard Interactivo
- Resumen en tiempo real de deducciones por categoría
- Gráficos de progreso y distribución
- Monitoreo de límites anuales SRI 2025
- Interfaz moderna tipo Mint/YNAB

### 🧾 Procesamiento Automático de Facturas
- **OCR Avanzado**: Google Vision API para extraer texto de imágenes y PDFs
- **IA Inteligente**: OpenAI para procesar y estructurar datos
- **Validación SRI**: Verificación automática según reglas Ecuador 2025
- **Categorización**: Clasificación automática en 5 categorías SRI

### 📈 Gestión Completa
- Almacenamiento en Google Sheets
- Reportes diarios y mensuales
- Seguimiento de presupuestos
- Gestión de deudas
- Estado SRI en tiempo real

## 🏗️ Estructura del Proyecto

```
finanzas-sri-ecuador/
├── app.py                 # Aplicación Flask principal
├── config.py             # Configuración y constantes SRI
├── requirements.txt      # Dependencias Python
├── .env.example         # Variables de entorno
├── README.md           # Documentación
├── utils/              # Módulos de utilidades
│   ├── ocr_processor.py      # Procesamiento OCR
│   ├── openai_processor.py   # Análisis con IA
│   ├── sheets_manager.py     # Gestión Google Sheets
│   └── sri_validator.py      # Validación reglas SRI
├── templates/          # Templates HTML
│   ├── base.html            # Template base
│   ├── dashboard.html       # Dashboard principal
│   ├── upload.html          # Subir facturas
│   └── transactions.html    # Historial
└── static/            # Archivos estáticos
    ├── css/style.css       # Estilos personalizados
    ├── js/app.js          # JavaScript principal
    └── images/            # Imágenes del sistema
```

## 🚀 Instalación y Configuración

### 1. Prerequisitos
- Python 3.8+
- Cuenta Google Cloud (para OCR)
- API Key de OpenAI
- Google Sheets API habilitada

### 2. Clonación del Repositorio
```bash
git clone https://github.com/earauzt/finanzas-sri-ecuador.git
cd finanzas-sri-ecuador
```

### 3. Entorno Virtual
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 4. Instalación de Dependencias
```bash
pip install -r requirements.txt
```

### 5. Configuración de Variables de Entorno
```bash
cp .env.example .env
```

Edita `.env` con tus credenciales:
```env
# Flask
SECRET_KEY=tu-clave-secreta-muy-segura

# Google Cloud Vision API
GOOGLE_APPLICATION_CREDENTIALS=ruta/a/tu/google-credentials.json

# OpenAI API
OPENAI_API_KEY=tu-openai-api-key

# Google Sheets API
GOOGLE_SHEETS_CREDENTIALS=ruta/a/tu/sheets-credentials.json
SPREADSHEET_ID=tu-google-sheets-id
```

### 6. Configuración de APIs

#### Google Cloud Vision API
1. Ir a [Google Cloud Console](https://console.cloud.google.com/)
2. Crear proyecto o seleccionar existente
3. Habilitar Vision API
4. Crear credenciales de servicio
5. Descargar archivo JSON

#### OpenAI API
1. Crear cuenta en [OpenAI](https://platform.openai.com/)
2. Generar API Key
3. Configurar límites de uso

#### Google Sheets API
1. Habilitar Google Sheets API en Google Cloud
2. Crear credenciales de servicio
3. Compartir hoja de cálculo con email del servicio
4. Copiar ID de la hoja de cálculo

### 7. Ejecutar la Aplicación
```bash
python app.py
```

La aplicación estará disponible en `http://localhost:5000`

## 💰 Categorías SRI Ecuador 2025

| Categoría | Límite Anual | Porcentaje | Descripción |
|-----------|--------------|------------|-------------|
| 🍽️ **Alimentación** | $5,252.59 | 10% | Alimentos para consumo humano |
| 🏥 **Salud** | $4,394.10 | 15% | Gastos médicos y medicina |
| 👕 **Vestimenta** | $1,976.29 | 5% | Prendas de vestir |
| 🏠 **Vivienda** | $1,097.97 | 3% | Arriendo, servicios básicos |
| 🎓 **Educación** | $4,394.10 | 15% | Educación, arte y cultura |

**Límite Total Anual: $14,753.40**

## 📱 Uso del Sistema

### 1. Subir Facturas
1. Navegar a "Subir Factura"
2. Arrastrar imagen/PDF o hacer clic para seleccionar
3. El sistema automáticamente:
   - Extrae texto con OCR
   - Analiza datos con IA
   - Valida según reglas SRI
   - Categoriza la factura
   - Guarda en Google Sheets

### 2. Dashboard
- Ver progreso en tiempo real
- Gráficos interactivos por categoría
- Estadísticas de uso
- Límites restantes

### 3. Historial de Transacciones
- Filtrar por fecha y categoría
- Ver detalles completos
- Editar información
- Exportar datos

### 4. Reportes
- Reporte diario de gastos
- Resumen mensual
- Estado SRI actualizado
- Proyecciones anuales

## 🔧 Configuración Avanzada

### Personalizar Límites SRI
Editar `config.py`:
```python
SRI_DEDUCTIONS = {
    'ALIMENTACION': {
        'max_deduction': 5252.59,
        'percentage': 0.10,
        'description': 'Alimentos para consumo humano'
    },
    # ... otras categorías
}
```

### Agregar Nuevas Validaciones
Modificar `utils/sri_validator.py` para agregar reglas específicas.

### Customizar Interfaz
Modificar `static/css/style.css` para cambiar colores y estilos.

## 🐛 Solución de Problemas

### Error de OCR
- Verificar credenciales de Google Cloud
- Confirmar que Vision API está habilitada
- Revisar formato de imagen (JPG, PNG, PDF)

### Error de OpenAI
- Verificar API Key válida
- Confirmar saldo disponible
- Revisar límites de uso

### Error de Google Sheets
- Verificar permisos de la hoja
- Confirmar que el servicio tiene acceso
- Revisar ID de la hoja

## 📄 Formatos de Archivo Soportados

### Imágenes
- **JPG/JPEG**: Recomendado para fotos de facturas
- **PNG**: Ideal para capturas de pantalla

### Documentos
- **PDF**: Facturas electrónicas y documentos escaneados

### Límites
- **Tamaño máximo**: 16MB por archivo
- **Resolución**: Mínimo 1000x1000 píxeles para mejor OCR

## 🔒 Seguridad

### Datos Personales
- Todas las APIs usan HTTPS
- Credenciales almacenadas localmente
- Sin almacenamiento de imágenes permanente

### Recomendaciones
- Usar claves API con permisos mínimos
- Revisar regularmente accesos
- Mantener credenciales actualizadas

## 🤝 Contribuciones

1. Fork del repositorio
2. Crear branch para feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push al branch (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## 📜 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 🆘 Soporte

- **Issues**: [GitHub Issues](https://github.com/earauzt/finanzas-sri-ecuador/issues)
- **Email**: tu-email@ejemplo.com
- **Documentación**: [Wiki del proyecto](https://github.com/earauzt/finanzas-sri-ecuador/wiki)

## 🚗 Roadmap

### v2.0 (Próximamente)
- [ ] Integración con bancos ecuatorianos
- [ ] App móvil
- [ ] Alertas automáticas por WhatsApp
- [ ] Exportación a formatos SRI oficiales

### v2.1 (Futuro)
- [ ] Machine Learning para mejor categorización
- [ ] Integración con sistemas contables
- [ ] API pública para desarrolladores
- [ ] Soporte para múltiples años fiscales

---

**Desarrollado con ❤️ para la comunidad ecuatoriana**

*Sistema conforme a las regulaciones SRI Ecuador 2025* 