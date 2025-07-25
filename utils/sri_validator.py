import re
from datetime import datetime, date
from config import Config

class SRIValidator:
    def __init__(self):
        """Inicializar validador SRI Ecuador 2025"""
        self.current_year = datetime.now().year
        
        # Patrones de validación
        self.ruc_pattern = re.compile(r'^\d{13}$')
        self.authorization_pattern = re.compile(r'^\d{10,49}$')
        
        # Lista de establecimientos válidos para deducciones
        self.valid_establishments = {
            'ALIMENTACION': [
                'supermercados', 'tiendas', 'mercados', 'minimarket',
                'panadería', 'carnicería', 'verdulería', 'lacteos'
            ],
            'SALUD': [
                'farmacia', 'hospital', 'clínica', 'laboratorio',
                'consultorio', 'óptica', 'dental'
            ],
            'VESTIMENTA': [
                'almacén', 'boutique', 'zapatería', 'ropa',
                'textil', 'confecciones'
            ],
            'VIVIENDA': [
                'ferretería', 'pinturas', 'materiales', 'construcción',
                'mueblería', 'decoración', 'electrodomésticos'
            ],
            'EDUCACION': [
                'librería', 'papelería', 'universidad', 'colegio',
                'instituto', 'academia', 'escuela'
            ]
        }
        
        # Códigos de actividad económica permitidos
        self.allowed_activity_codes = {
            'ALIMENTACION': ['G471', 'G472', 'G478', 'C101', 'C102'],
            'SALUD': ['Q861', 'Q862', 'G477', 'Q869'],
            'VESTIMENTA': ['G474', 'C131', 'C141', 'C151'],
            'VIVIENDA': ['G474', 'C251', 'C271', 'F41'],
            'EDUCACION': ['G476', 'P851', 'P852', 'P853']
        }
    
    def validate_receipt(self, receipt_data):
        """
        Validar factura según reglas SRI Ecuador 2025
        """
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'deductible_amount': 0,
            'category': receipt_data.get('sri_category', 'ALIMENTACION')
        }
        
        # Validaciones básicas
        self._validate_basic_info(receipt_data, validation_result)
        
        # Validar RUC
        self._validate_ruc(receipt_data, validation_result)
        
        # Validar autorización SRI
        self._validate_authorization(receipt_data, validation_result)
        
        # Validar fecha
        self._validate_date(receipt_data, validation_result)
        
        # Validar montos
        self._validate_amounts(receipt_data, validation_result)
        
        # Validar categoría SRI
        self._validate_sri_category(receipt_data, validation_result)
        
        # Validar límites de deducción
        self._validate_deduction_limits(receipt_data, validation_result)
        
        # Validar establecimiento
        self._validate_establishment(receipt_data, validation_result)
        
        # Determinar si es válida
        validation_result['valid'] = len(validation_result['errors']) == 0
        
        # Calcular monto deducible
        if validation_result['valid']:
            validation_result['deductible_amount'] = self._calculate_deductible_amount(receipt_data)
        
        return validation_result
    
    def _validate_basic_info(self, receipt_data, result):
        """Validar información básica requerida"""
        required_fields = ['merchant_name', 'total_amount', 'date']
        
        for field in required_fields:
            if not receipt_data.get(field):
                result['errors'].append(f"Campo requerido faltante: {field}")
    
    def _validate_ruc(self, receipt_data, result):
        """Validar RUC del emisor"""
        ruc = receipt_data.get('ruc', '')
        
        if not ruc:
            result['warnings'].append("RUC no encontrado en la factura")
            return
        
        # Remover caracteres no numéricos
        ruc_clean = re.sub(r'[^0-9]', '', ruc)
        
        if not self.ruc_pattern.match(ruc_clean):
            result['errors'].append("RUC inválido: debe tener 13 dígitos")
            return
        
        # Validar dígito verificador
        if not self._validate_ruc_check_digit(ruc_clean):
            result['errors'].append("RUC inválido: dígito verificador incorrecto")
    
    def _validate_ruc_check_digit(self, ruc):
        """Validar dígito verificador del RUC"""
        try:
            # Algoritmo de validación RUC Ecuador
            if len(ruc) != 13:
                return False
            
            # Personas naturales
            if ruc[2] in ['0', '1', '2', '3', '4', '5']:
                coefficients = [2, 1, 2, 1, 2, 1, 2, 1, 2]
                total = 0
                
                for i in range(9):
                    product = int(ruc[i]) * coefficients[i]
                    if product >= 10:
                        product = product // 10 + product % 10
                    total += product
                
                check_digit = (10 - (total % 10)) % 10
                return int(ruc[9]) == check_digit
            
            # Empresas privadas
            elif ruc[2] == '9':
                coefficients = [4, 3, 2, 7, 6, 5, 4, 3, 2]
                total = sum(int(ruc[i]) * coefficients[i] for i in range(9))
                check_digit = 11 - (total % 11)
                if check_digit == 11:
                    check_digit = 0
                elif check_digit == 10:
                    return False
                return int(ruc[9]) == check_digit
            
            return True
            
        except:
            return False
    
    def _validate_authorization(self, receipt_data, result):
        """Validar número de autorización SRI"""
        auth_number = receipt_data.get('authorization_number', '')
        
        if not auth_number:
            result['warnings'].append("Número de autorización no encontrado")
            return
        
        # Remover caracteres no numéricos
        auth_clean = re.sub(r'[^0-9]', '', auth_number)
        
        if not self.authorization_pattern.match(auth_clean):
            result['errors'].append("Número de autorización inválido")
    
    def _validate_date(self, receipt_data, result):
        """Validar fecha de la factura"""
        date_str = receipt_data.get('date', '')
        
        if not date_str:
            result['errors'].append("Fecha de factura requerida")
            return
        
        try:
            receipt_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            current_date = date.today()
            
            # No puede ser fecha futura
            if receipt_date > current_date:
                result['errors'].append("La fecha no puede ser futura")
            
            # No puede ser muy antigua (más de 1 año)
            days_diff = (current_date - receipt_date).days
            if days_diff > 365:
                result['errors'].append("Factura muy antigua (más de 1 año)")
            
            # Debe ser del año fiscal actual o anterior
            if receipt_date.year < self.current_year - 1:
                result['errors'].append("Factura fuera del período fiscal válido")
                
        except ValueError:
            result['errors'].append("Formato de fecha inválido")
    
    def _validate_amounts(self, receipt_data, result):
        """Validar montos de la factura"""
        total = receipt_data.get('total_amount', 0)
        subtotal = receipt_data.get('subtotal', 0)
        iva = receipt_data.get('iva', 0)
        
        if total <= 0:
            result['errors'].append("Monto total debe ser mayor a 0")
            return
        
        # Validar coherencia de montos
        if subtotal > 0 and iva > 0:
            expected_total = subtotal + iva
            tolerance = 0.05  # 5 centavos de tolerancia
            
            if abs(total - expected_total) > tolerance:
                result['warnings'].append("Inconsistencia en cálculo de IVA")
        
        # Validar límite máximo por factura
        max_single_receipt = 5000.00  # Límite ejemplo
        if total > max_single_receipt:
            result['warnings'].append(f"Factura supera límite recomendado de ${max_single_receipt}")
    
    def _validate_sri_category(self, receipt_data, result):
        """Validar categoría SRI asignada"""
        category = receipt_data.get('sri_category', '')
        
        if category not in Config.SRI_DEDUCTIONS:
            result['errors'].append("Categoría SRI inválida")
            return
        
        # Validar coherencia con el tipo de comercio
        merchant_name = receipt_data.get('merchant_name', '').lower()
        valid_keywords = self.valid_establishments.get(category, [])
        
        # Verificar si el nombre del comercio coincide con la categoría
        category_match = any(keyword in merchant_name for keyword in valid_keywords)
        
        if not category_match:
            result['warnings'].append(f"El comercio no parece corresponder a la categoría {category}")
    
    def _validate_deduction_limits(self, receipt_data, result):
        """Validar límites de deducción"""
        category = receipt_data.get('sri_category', '')
        amount = receipt_data.get('total_amount', 0)
        
        if category not in Config.SRI_DEDUCTIONS:
            return
        
        category_config = Config.SRI_DEDUCTIONS[category]
        max_deduction = category_config['max_deduction']
        
        # Aquí deberíamos consultar el total ya usado en esta categoría
        # Por simplicidad, asumimos que esta validación se hace a nivel de aplicación
        
        if amount > max_deduction:
            result['warnings'].append(
                f"Monto excede límite anual para {category}: ${max_deduction}"
            )
    
    def _validate_establishment(self, receipt_data, result):
        """Validar tipo de establecimiento"""
        merchant_name = receipt_data.get('merchant_name', '').lower()
        category = receipt_data.get('sri_category', '')
        
        # Lista de establecimientos no permitidos para deducciones
        forbidden_keywords = [
            'bar', 'discoteca', 'casino', 'licores', 'cigarrillos',
            'combustible', 'gasolina', 'servicios profesionales'
        ]
        
        for forbidden in forbidden_keywords:
            if forbidden in merchant_name:
                result['errors'].append(
                    f"Establecimiento no permitido para deducciones: {forbidden}"
                )
                break
    
    def _calculate_deductible_amount(self, receipt_data):
        """Calcular monto deducible según reglas SRI"""
        total_amount = receipt_data.get('total_amount', 0)
        category = receipt_data.get('sri_category', '')
        
        if category not in Config.SRI_DEDUCTIONS:
            return 0
        
        # El monto deducible es el total de la factura
        # (las limitaciones se aplican a nivel anual)
        return total_amount
    
    def validate_annual_limits(self, category, current_used, new_amount):
        """Validar límites anuales de deducción"""
        if category not in Config.SRI_DEDUCTIONS:
            return {
                'valid': False,
                'message': 'Categoría inválida',
                'allowed_amount': 0
            }
        
        category_config = Config.SRI_DEDUCTIONS[category]
        max_deduction = category_config['max_deduction']
        
        total_after = current_used + new_amount
        
        if total_after <= max_deduction:
            return {
                'valid': True,
                'message': 'Dentro del límite',
                'allowed_amount': new_amount
            }
        else:
            allowed_amount = max(0, max_deduction - current_used)
            return {
                'valid': False,
                'message': f'Excede límite anual de ${max_deduction}',
                'allowed_amount': allowed_amount
            } 