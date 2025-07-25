import os
import io
from PIL import Image
import pdfplumber
from google.cloud import vision
from config import Config

class OCRProcessor:
    def __init__(self):
        """Inicializar cliente de Google Vision API"""
        if Config.GOOGLE_APPLICATION_CREDENTIALS:
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = Config.GOOGLE_APPLICATION_CREDENTIALS
            self.client = vision.ImageAnnotatorClient()
        else:
            self.client = None
            print("Advertencia: Google Vision API no configurada")
    
    def extract_text(self, file_path):
        """
        Extraer texto de imagen o PDF
        """
        try:
            if file_path.lower().endswith('.pdf'):
                return self._extract_text_from_pdf(file_path)
            else:
                return self._extract_text_from_image(file_path)
        except Exception as e:
            print(f"Error extrayendo texto: {str(e)}")
            return ""
    
    def _extract_text_from_image(self, image_path):
        """Extraer texto de imagen usando Google Vision API"""
        if not self.client:
            return "Google Vision API no configurada"
        
        try:
            with io.open(image_path, 'rb') as image_file:
                content = image_file.read()
            
            image = vision.Image(content=content)
            
            # Detectar texto
            response = self.client.text_detection(image=image)
            texts = response.text_annotations
            
            if texts:
                return texts[0].description
            else:
                return ""
                
        except Exception as e:
            print(f"Error en Google Vision API: {str(e)}")
            return ""
    
    def _extract_text_from_pdf(self, pdf_path):
        """Extraer texto de PDF"""
        try:
            text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return text
        except Exception as e:
            print(f"Error extrayendo texto del PDF: {str(e)}")
            return ""
    
    def preprocess_image(self, image_path):
        """Preprocesar imagen para mejorar OCR"""
        try:
            with Image.open(image_path) as img:
                # Convertir a escala de grises
                if img.mode != 'L':
                    img = img.convert('L')
                
                # Redimensionar si es muy pequeña
                width, height = img.size
                if width < 1000 or height < 1000:
                    factor = max(1000/width, 1000/height)
                    new_width = int(width * factor)
                    new_height = int(height * factor)
                    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # Guardar imagen preprocesada
                processed_path = image_path.replace('.', '_processed.')
                img.save(processed_path)
                return processed_path
        except Exception as e:
            print(f"Error preprocesando imagen: {str(e)}")
            return image_path 