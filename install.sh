#!/bin/bash

echo "🚀 Instalando Sistema de Finanzas SRI Ecuador"
echo "============================================="

# Actualizar pip
echo "📦 Actualizando pip..."
python3 -m pip install --upgrade pip

# Instalar dependencias
echo "📚 Instalando dependencias..."
pip3 install -r requirements.txt

# Crear directorio uploads si no existe
echo "📁 Creando directorios necesarios..."
mkdir -p uploads
mkdir -p static/images

# Verificar instalación
echo "✅ Verificando instalación..."
python3 -c "import flask; print('✅ Flask instalado correctamente')"
python3 -c "import requests; print('✅ Requests instalado correctamente')"
python3 -c "import pandas; print('✅ Pandas instalado correctamente')"

echo ""
echo "🎉 ¡Instalación completada!"
echo "📍 Para ejecutar: python3 main.py"
echo "🌐 La aplicación estará en: http://localhost:3000"
echo "" 