#!/usr/bin/env python3
"""
Finanzas SRI Ecuador - Punto de entrada para Replit
"""

import os
import sys

# Agregar el directorio actual al PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importar y ejecutar la aplicación
from app import app

if __name__ == '__main__':
    # Configuración específica para Replit
    port = int(os.environ.get('PORT', 3000))
    host = os.environ.get('HOST', '0.0.0.0')
    
    print(f"🚀 Iniciando aplicación en {host}:{port}")
    print("📊 Sistema de Finanzas SRI Ecuador")
    print("=" * 50)
    
    app.run(
        host=host,
        port=port,
        debug=True,
        threaded=True
    ) 