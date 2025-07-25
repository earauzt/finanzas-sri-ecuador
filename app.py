from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_cors import CORS
import os
from datetime import datetime, date
import json
from config import Config
from utils.ocr_processor import OCRProcessor
from utils.openai_processor import OpenAIProcessor
from utils.sheets_manager import SheetsManager
from utils.sri_validator import SRIValidator

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# Crear directorio de uploads si no existe
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Inicializar servicios
ocr_processor = OCRProcessor()
openai_processor = OpenAIProcessor()
sheets_manager = SheetsManager()
sri_validator = SRIValidator()

@app.route('/')
def index():
    """Dashboard principal"""
    try:
        # Si está en modo demostración, usar datos de ejemplo
        if Config.DEMO_MODE:
            # Datos de demostración para mostrar funcionalidad
            demo_deductions = {
                'ALIMENTACION': 1200.50,
                'SALUD': 650.30,
                'VESTIMENTA': 300.00,
                'VIVIENDA': 200.00,
                'EDUCACION': 100.00
            }
            deductions_data = demo_deductions
        else:
            # Obtener datos reales de Google Sheets
            deductions_data = sheets_manager.get_current_deductions()
        
        # Calcular estadísticas
        stats = {
            'total_used': sum(deductions_data.values()),
            'total_available': Config.TOTAL_DEDUCTION_LIMIT,
            'categories': {}
        }
        
        # Calcular por categorías
        for category, config in Config.SRI_DEDUCTIONS.items():
            used = deductions_data.get(category, 0)
            available = config['max_deduction']
            percentage = (used / available * 100) if available > 0 else 0
            
            stats['categories'][category] = {
                'used': used,
                'available': available,
                'percentage': min(percentage, 100),
                'description': config['description']
            }
        
        return render_template('dashboard.html', stats=stats, demo_mode=Config.DEMO_MODE)
    except Exception as e:
        app.logger.error(f"Error en dashboard: {str(e)}")
        return render_template('dashboard.html', stats=None, error=str(e))

@app.route('/transactions')
def transactions():
    """Página de transacciones"""
    try:
        if Config.DEMO_MODE:
            # Datos de demostración para transacciones
            demo_transactions = [
                {
                    'Fecha': '2025-01-15',
                    'Comerciante': 'Supermaxi',
                    'RUC': '1790011674001',
                    'Monto Total': 45.80,
                    'Subtotal': 40.89,
                    'IVA': 4.91,
                    'Categoría SRI': 'ALIMENTACION',
                    'Deducible': 'SÍ',
                    'Autorización': '1234567890123456789',
                    'Descripción': 'Productos alimenticios básicos (x15)',
                    'Fecha Procesamiento': '2025-01-15T10:30:00'
                },
                {
                    'Fecha': '2025-01-14',
                    'Comerciante': 'Farmacia Cruz Azul',
                    'RUC': '1790016919001',
                    'Monto Total': 28.50,
                    'Subtotal': 25.45,
                    'IVA': 3.05,
                    'Categoría SRI': 'SALUD',
                    'Deducible': 'SÍ',
                    'Autorización': '9876543210987654321',
                    'Descripción': 'Medicamentos recetados (x3)',
                    'Fecha Procesamiento': '2025-01-14T16:45:00'
                },
                {
                    'Fecha': '2025-01-13',
                    'Comerciante': 'De Prati',
                    'RUC': '1790344451001',
                    'Monto Total': 89.99,
                    'Subtotal': 80.35,
                    'IVA': 9.64,
                    'Categoría SRI': 'VESTIMENTA',
                    'Deducible': 'SÍ',
                    'Autorización': '5555666677778888999',
                    'Descripción': 'Camisa formal (x1)',
                    'Fecha Procesamiento': '2025-01-13T12:15:00'
                }
            ]
            transactions_data = demo_transactions
        else:
            transactions_data = sheets_manager.get_transactions()
        return render_template('transactions.html', transactions=transactions_data, demo_mode=Config.DEMO_MODE)
    except Exception as e:
        app.logger.error(f"Error en transacciones: {str(e)}")
        return render_template('transactions.html', transactions=[], error=str(e))

@app.route('/budgets')
def budgets():
    """Página de presupuestos"""
    return render_template('budgets.html')

@app.route('/daily-report')
def daily_report():
    """Reporte diario"""
    try:
        daily_data = sheets_manager.get_daily_report()
        return render_template('daily_report.html', data=daily_data)
    except Exception as e:
        app.logger.error(f"Error en reporte diario: {str(e)}")
        return render_template('daily_report.html', data=None, error=str(e))

@app.route('/monthly')
def monthly():
    """Reporte mensual"""
    try:
        monthly_data = sheets_manager.get_monthly_report()
        return render_template('monthly_report.html', data=monthly_data)
    except Exception as e:
        app.logger.error(f"Error en reporte mensual: {str(e)}")
        return render_template('monthly_report.html', data=None, error=str(e))

@app.route('/deudas')
def deudas():
    """Página de deudas"""
    return render_template('deudas.html')

@app.route('/sri-status')
def sri_status():
    """Estado SRI"""
    try:
        sri_data = sheets_manager.get_sri_status()
        return render_template('sri_status.html', data=sri_data)
    except Exception as e:
        app.logger.error(f"Error en estado SRI: {str(e)}")
        return render_template('sri_status.html', data=None, error=str(e))

@app.route('/upload', methods=['GET', 'POST'])
def upload_receipt():
    """Subir factura para procesamiento"""
    if request.method == 'GET':
        return render_template('upload.html')
    
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No se seleccionó archivo'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No se seleccionó archivo'}), 400
        
        if not Config.allowed_file(file.filename):
            return jsonify({'error': 'Tipo de archivo no permitido'}), 400
        
        # Guardar archivo
        filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Procesar con OCR
        extracted_text = ocr_processor.extract_text(filepath)
        
        # Procesar con OpenAI
        processed_data = openai_processor.process_receipt(extracted_text)
        
        # Validar con reglas SRI
        validation_result = sri_validator.validate_receipt(processed_data)
        
        if validation_result['valid']:
            # Guardar en Google Sheets
            sheets_manager.save_transaction(processed_data)
            
            return jsonify({
                'success': True,
                'data': processed_data,
                'message': 'Factura procesada exitosamente'
            })
        else:
            return jsonify({
                'success': False,
                'error': validation_result['message'],
                'data': processed_data
            })
    
    except Exception as e:
        app.logger.error(f"Error procesando factura: {str(e)}")
        return jsonify({'error': f'Error procesando factura: {str(e)}'}), 500

@app.route('/api/stats')
def api_stats():
    """API para obtener estadísticas en tiempo real"""
    try:
        deductions_data = sheets_manager.get_current_deductions()
        
        stats = {
            'total_used': sum(deductions_data.values()),
            'total_available': Config.TOTAL_DEDUCTION_LIMIT,
            'categories': {}
        }
        
        for category, config in Config.SRI_DEDUCTIONS.items():
            used = deductions_data.get(category, 0)
            available = config['max_deduction']
            percentage = (used / available * 100) if available > 0 else 0
            
            stats['categories'][category] = {
                'used': used,
                'available': available,
                'percentage': min(percentage, 100),
                'description': config['description']
            }
        
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/validate-receipt', methods=['POST'])
def api_validate_receipt():
    """API para validar una factura manualmente"""
    try:
        data = request.get_json()
        validation_result = sri_validator.validate_receipt(data)
        return jsonify(validation_result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    # Configuración para diferentes entornos
    port = int(os.environ.get('PORT', 3000))
    host = os.environ.get('HOST', '0.0.0.0')
    debug = os.environ.get('FLASK_DEBUG', 'true').lower() == 'true'
    
    print("🚀 Iniciando Sistema de Finanzas SRI Ecuador")
    print(f"📍 Servidor: http://{host}:{port}")
    print("📊 Dashboard de Deducciones SRI 2025")
    print("=" * 50)
    
    app.run(
        host=host,
        port=port,
        debug=debug,
        threaded=True
    ) 