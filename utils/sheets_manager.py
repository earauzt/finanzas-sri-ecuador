import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from datetime import datetime, timedelta
import json
from config import Config

class SheetsManager:
    def __init__(self):
        """Inicializar cliente de Google Sheets"""
        try:
            if Config.GOOGLE_SHEETS_CREDENTIALS and Config.SPREADSHEET_ID:
                scope = ['https://spreadsheets.google.com/feeds',
                        'https://www.googleapis.com/auth/drive']
                
                # Cargar credenciales desde archivo JSON
                creds = ServiceAccountCredentials.from_json_keyfile_name(
                    Config.GOOGLE_SHEETS_CREDENTIALS, scope)
                
                self.client = gspread.authorize(creds)
                self.spreadsheet = self.client.open_by_key(Config.SPREADSHEET_ID)
                
                # Inicializar hojas si no existen
                self._initialize_sheets()
            else:
                self.client = None
                self.spreadsheet = None
                print("Advertencia: Google Sheets no configurado")
        except Exception as e:
            print(f"Error configurando Google Sheets: {str(e)}")
            self.client = None
            self.spreadsheet = None
    
    def _initialize_sheets(self):
        """Inicializar estructura de hojas de cálculo"""
        try:
            # Crear hoja de transacciones si no existe
            try:
                self.transactions_sheet = self.spreadsheet.worksheet("Transacciones")
            except gspread.WorksheetNotFound:
                self.transactions_sheet = self.spreadsheet.add_worksheet(
                    title="Transacciones", rows=1000, cols=20)
                
                # Agregar encabezados
                headers = [
                    "Fecha", "Comerciante", "RUC", "Monto Total", "Subtotal", 
                    "IVA", "Categoría SRI", "Deducible", "Autorización", 
                    "Descripción", "Fecha Procesamiento"
                ]
                self.transactions_sheet.insert_row(headers, 1)
            
            # Crear hoja de resumen si no existe
            try:
                self.summary_sheet = self.spreadsheet.worksheet("Resumen")
            except gspread.WorksheetNotFound:
                self.summary_sheet = self.spreadsheet.add_worksheet(
                    title="Resumen", rows=100, cols=10)
                
                # Agregar estructura básica de resumen
                self._setup_summary_sheet()
                
        except Exception as e:
            print(f"Error inicializando hojas: {str(e)}")
    
    def _setup_summary_sheet(self):
        """Configurar hoja de resumen con estructura básica"""
        try:
            # Encabezados y estructura
            data = [
                ["RESUMEN DEDUCCIONES SRI 2025", "", "", ""],
                ["", "", "", ""],
                ["Categoría", "Usado", "Disponible", "Porcentaje"],
                ["ALIMENTACION", "=SUMIF(Transacciones!G:G,\"ALIMENTACION\",Transacciones!D:D)", "5252.59", "=B4/C4*100"],
                ["SALUD", "=SUMIF(Transacciones!G:G,\"SALUD\",Transacciones!D:D)", "4394.10", "=B5/C5*100"],
                ["VESTIMENTA", "=SUMIF(Transacciones!G:G,\"VESTIMENTA\",Transacciones!D:D)", "1976.29", "=B6/C6*100"],
                ["VIVIENDA", "=SUMIF(Transacciones!G:G,\"VIVIENDA\",Transacciones!D:D)", "1097.97", "=B7/C7*100"],
                ["EDUCACION", "=SUMIF(Transacciones!G:G,\"EDUCACION\",Transacciones!D:D)", "4394.10", "=B8/C8*100"],
                ["", "", "", ""],
                ["TOTAL USADO", "=SUM(B4:B8)", "", ""],
                ["LÍMITE TOTAL", "14753.40", "", ""],
                ["DISPONIBLE", "=B11-B10", "", ""]
            ]
            
            for i, row in enumerate(data, 1):
                self.summary_sheet.insert_row(row, i)
                
        except Exception as e:
            print(f"Error configurando hoja de resumen: {str(e)}")
    
    def save_transaction(self, transaction_data):
        """Guardar transacción en Google Sheets"""
        if not self.transactions_sheet:
            print("Google Sheets no disponible")
            return False
        
        try:
            row_data = [
                transaction_data.get('date', ''),
                transaction_data.get('merchant_name', ''),
                transaction_data.get('ruc', ''),
                transaction_data.get('total_amount', 0),
                transaction_data.get('subtotal', 0),
                transaction_data.get('iva', 0),
                transaction_data.get('sri_category', ''),
                'SÍ' if transaction_data.get('deductible', False) else 'NO',
                transaction_data.get('authorization_number', ''),
                self._get_items_description(transaction_data.get('items', [])),
                transaction_data.get('processed_date', datetime.now().isoformat())
            ]
            
            self.transactions_sheet.append_row(row_data)
            return True
            
        except Exception as e:
            print(f"Error guardando transacción: {str(e)}")
            return False
    
    def get_current_deductions(self):
        """Obtener deducciones actuales por categoría"""
        if not self.transactions_sheet:
            return {}
        
        try:
            # Obtener todas las transacciones
            records = self.transactions_sheet.get_all_records()
            
            deductions = {
                'ALIMENTACION': 0,
                'SALUD': 0,
                'VESTIMENTA': 0,
                'VIVIENDA': 0,
                'EDUCACION': 0
            }
            
            for record in records:
                category = record.get('Categoría SRI', '')
                amount = float(record.get('Monto Total', 0) or 0)
                deductible = record.get('Deducible', '') == 'SÍ'
                
                if category in deductions and deductible:
                    deductions[category] += amount
            
            return deductions
            
        except Exception as e:
            print(f"Error obteniendo deducciones: {str(e)}")
            return {}
    
    def get_transactions(self, limit=50):
        """Obtener transacciones recientes"""
        if not self.transactions_sheet:
            return []
        
        try:
            records = self.transactions_sheet.get_all_records()
            
            # Ordenar por fecha de procesamiento (más reciente primero)
            sorted_records = sorted(records, 
                                  key=lambda x: x.get('Fecha Procesamiento', ''), 
                                  reverse=True)
            
            return sorted_records[:limit]
            
        except Exception as e:
            print(f"Error obteniendo transacciones: {str(e)}")
            return []
    
    def get_daily_report(self):
        """Obtener reporte diario"""
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            
            if not self.transactions_sheet:
                return {'date': today, 'total': 0, 'count': 0, 'categories': {}}
            
            records = self.transactions_sheet.get_all_records()
            
            daily_data = {
                'date': today,
                'total': 0,
                'count': 0,
                'categories': {}
            }
            
            for record in records:
                record_date = record.get('Fecha', '')
                if record_date.startswith(today):
                    amount = float(record.get('Monto Total', 0) or 0)
                    category = record.get('Categoría SRI', '')
                    
                    daily_data['total'] += amount
                    daily_data['count'] += 1
                    
                    if category not in daily_data['categories']:
                        daily_data['categories'][category] = 0
                    daily_data['categories'][category] += amount
            
            return daily_data
            
        except Exception as e:
            print(f"Error obteniendo reporte diario: {str(e)}")
            return {'date': datetime.now().strftime('%Y-%m-%d'), 'total': 0, 'count': 0, 'categories': {}}
    
    def get_monthly_report(self):
        """Obtener reporte mensual"""
        try:
            current_month = datetime.now().strftime('%Y-%m')
            
            if not self.transactions_sheet:
                return {'month': current_month, 'total': 0, 'count': 0, 'categories': {}}
            
            records = self.transactions_sheet.get_all_records()
            
            monthly_data = {
                'month': current_month,
                'total': 0,
                'count': 0,
                'categories': {}
            }
            
            for record in records:
                record_date = record.get('Fecha', '')
                if record_date.startswith(current_month):
                    amount = float(record.get('Monto Total', 0) or 0)
                    category = record.get('Categoría SRI', '')
                    
                    monthly_data['total'] += amount
                    monthly_data['count'] += 1
                    
                    if category not in monthly_data['categories']:
                        monthly_data['categories'][category] = 0
                    monthly_data['categories'][category] += amount
            
            return monthly_data
            
        except Exception as e:
            print(f"Error obteniendo reporte mensual: {str(e)}")
            return {'month': datetime.now().strftime('%Y-%m'), 'total': 0, 'count': 0, 'categories': {}}
    
    def get_sri_status(self):
        """Obtener estado de deducciones SRI"""
        try:
            deductions = self.get_current_deductions()
            
            status = {
                'total_used': sum(deductions.values()),
                'total_limit': Config.TOTAL_DEDUCTION_LIMIT,
                'categories': {}
            }
            
            for category, config in Config.SRI_DEDUCTIONS.items():
                used = deductions.get(category, 0)
                limit = config['max_deduction']
                percentage = (used / limit * 100) if limit > 0 else 0
                
                status['categories'][category] = {
                    'used': used,
                    'limit': limit,
                    'remaining': limit - used,
                    'percentage': min(percentage, 100),
                    'description': config['description']
                }
            
            return status
            
        except Exception as e:
            print(f"Error obteniendo estado SRI: {str(e)}")
            return {}
    
    def _get_items_description(self, items):
        """Crear descripción de items para la hoja"""
        if not items:
            return ""
        
        descriptions = []
        for item in items:
            desc = item.get('description', 'Item')
            qty = item.get('quantity', 1)
            descriptions.append(f"{desc} (x{qty})")
        
        return "; ".join(descriptions) 