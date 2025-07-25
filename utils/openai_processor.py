import openai
import json
from datetime import datetime
from config import Config

class OpenAIProcessor:
    def __init__(self):
        """Inicializar cliente de OpenAI"""
        if Config.OPENAI_API_KEY:
            openai.api_key = Config.OPENAI_API_KEY
            self.client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
        else:
            self.client = None
            print("Advertencia: OpenAI API no configurada")
    
    def process_receipt(self, extracted_text):
        """
        Procesar texto extraído de factura y estructurar datos
        """
        if not self.client:
            return self._fallback_processing(extracted_text)
        
        try:
            prompt = self._create_processing_prompt(extracted_text)
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Eres un asistente especializado en procesar facturas ecuatorianas para deducciones SRI."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=1000
            )
            
            result = response.choices[0].message.content
            
            # Intentar parsear como JSON
            try:
                data = json.loads(result)
                return self._validate_and_clean_data(data)
            except json.JSONDecodeError:
                # Si no es JSON válido, crear estructura básica
                return self._create_basic_structure(extracted_text)
                
        except Exception as e:
            print(f"Error en OpenAI: {str(e)}")
            return self._fallback_processing(extracted_text)
    
    def _create_processing_prompt(self, text):
        """Crear prompt para procesar la factura"""
        return f"""
        Analiza el siguiente texto de una factura ecuatoriana y extrae la información en formato JSON.
        
        Texto de la factura:
        {text}
        
        Extrae la siguiente información y devuélvela en formato JSON:
        {{
            "merchant_name": "nombre del comerciante",
            "ruc": "RUC del comerciante",
            "date": "fecha de la factura (YYYY-MM-DD)",
            "total_amount": monto_total_numerico,
            "subtotal": subtotal_numerico,
            "iva": iva_numerico,
            "items": [
                {{
                    "description": "descripción del producto/servicio",
                    "quantity": cantidad_numerica,
                    "unit_price": precio_unitario_numerico,
                    "total": total_item_numerico
                }}
            ],
            "sri_category": "ALIMENTACION|SALUD|VESTIMENTA|VIVIENDA|EDUCACION",
            "deductible": true|false,
            "authorization_number": "número de autorización SRI"
        }}
        
        Reglas importantes:
        1. Si no encuentras un dato, usa null
        2. Los montos deben ser números, no strings
        3. La categoría SRI debe ser una de las 5 opciones listadas
        4. La fecha debe estar en formato YYYY-MM-DD
        5. Solo devuelve el JSON, sin texto adicional
        """
    
    def _validate_and_clean_data(self, data):
        """Validar y limpiar datos procesados"""
        # Valores por defecto
        cleaned_data = {
            "merchant_name": data.get("merchant_name", ""),
            "ruc": data.get("ruc", ""),
            "date": data.get("date", datetime.now().strftime("%Y-%m-%d")),
            "total_amount": float(data.get("total_amount", 0)),
            "subtotal": float(data.get("subtotal", 0)),
            "iva": float(data.get("iva", 0)),
            "items": data.get("items", []),
            "sri_category": data.get("sri_category", "ALIMENTACION"),
            "deductible": data.get("deductible", True),
            "authorization_number": data.get("authorization_number", ""),
            "processed_date": datetime.now().isoformat()
        }
        
        # Validar categoría SRI
        valid_categories = ['ALIMENTACION', 'SALUD', 'VESTIMENTA', 'VIVIENDA', 'EDUCACION']
        if cleaned_data["sri_category"] not in valid_categories:
            cleaned_data["sri_category"] = "ALIMENTACION"
        
        # Validar fecha
        try:
            datetime.strptime(cleaned_data["date"], "%Y-%m-%d")
        except:
            cleaned_data["date"] = datetime.now().strftime("%Y-%m-%d")
        
        return cleaned_data
    
    def _fallback_processing(self, text):
        """Procesamiento básico sin OpenAI"""
        return {
            "merchant_name": "Procesamiento manual requerido",
            "ruc": "",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "total_amount": 0.0,
            "subtotal": 0.0,
            "iva": 0.0,
            "items": [],
            "sri_category": "ALIMENTACION",
            "deductible": False,
            "authorization_number": "",
            "processed_date": datetime.now().isoformat(),
            "raw_text": text
        }
    
    def _create_basic_structure(self, text):
        """Crear estructura básica cuando no se puede parsear JSON"""
        # Intentar extraer monto total con regex simple
        import re
        
        total_pattern = r'TOTAL[\s:]*\$?(\d+[.,]\d{2})'
        total_match = re.search(total_pattern, text, re.IGNORECASE)
        total_amount = float(total_match.group(1).replace(',', '.')) if total_match else 0.0
        
        return {
            "merchant_name": "Extraído de texto",
            "ruc": "",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "total_amount": total_amount,
            "subtotal": total_amount * 0.8929,  # Estimación básica
            "iva": total_amount * 0.1071,      # Estimación básica
            "items": [{"description": "Producto genérico", "quantity": 1, "unit_price": total_amount, "total": total_amount}],
            "sri_category": "ALIMENTACION",
            "deductible": True,
            "authorization_number": "",
            "processed_date": datetime.now().isoformat(),
            "raw_text": text
        } 