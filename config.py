import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Google Cloud Vision API
    GOOGLE_APPLICATION_CREDENTIALS = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
    
    # OpenAI API
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    
    # Google Sheets API
    GOOGLE_SHEETS_CREDENTIALS = os.environ.get('GOOGLE_SHEETS_CREDENTIALS')
    SPREADSHEET_ID = os.environ.get('SPREADSHEET_ID')
    
    # Upload Configuration
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
    
    # SRI Ecuador Configuration 2025
    SRI_DEDUCTIONS = {
        'ALIMENTACION': {
            'max_deduction': 5252.59,
            'percentage': 0.10,
            'description': 'Alimentos para consumo humano'
        },
        'SALUD': {
            'max_deduction': 4394.10,
            'percentage': 0.15,
            'description': 'Gastos médicos y medicina'
        },
        'VESTIMENTA': {
            'max_deduction': 1976.29,
            'percentage': 0.05,
            'description': 'Prendas de vestir'
        },
        'VIVIENDA': {
            'max_deduction': 1097.97,
            'percentage': 0.03,
            'description': 'Arriendo, servicios básicos'
        },
        'EDUCACION': {
            'max_deduction': 4394.10,
            'percentage': 0.15,
            'description': 'Educación, arte y cultura'
        }
    }
    
    # Límite total de deducciones
    TOTAL_DEDUCTION_LIMIT = 14753.40
    
    @staticmethod
    def allowed_file(filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS 