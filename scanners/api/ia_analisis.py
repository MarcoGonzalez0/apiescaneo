import os
import json
import logging
import requests
from dotenv import load_dotenv
from typing import Optional, Dict, List,Union,Any
from datetime import datetime

# -------------------- Configuración de Logging --------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('dorks_analyzer.log'),
        logging.StreamHandler()
    ]
)

# -------------------- Constantes --------------------
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_MODEL = "deepseek-chat"

# -------------------- Cargar variables de entorno --------------------
def load_env_variables() -> Optional[Dict[str, str]]:
    """Carga las variables de entorno necesarias"""
    load_dotenv()
    deepseek_api_key = os.getenv('DEEPSEEK_API_KEY')

    if not deepseek_api_key:
        logging.error("API Key de DeepSeek no encontrada en el archivo .env")
        return None

    logging.info("API Key de DeepSeek cargada correctamente")
    return {'deepseek_api_key': deepseek_api_key}

# -------------------- Cliente de DeepSeek --------------------
class DeepSeekClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def analyze_content(self, prompt: str, temperature: float = 0.3) -> Optional[str]:
        """Envía una solicitud a la API de DeepSeek para analizar contenido"""
        payload = {
            "model": DEEPSEEK_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": 2000
        }

        try:
            response = requests.post(
                DEEPSEEK_API_URL,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except requests.exceptions.RequestException as e:
            logging.error(f"Error en la API de DeepSeek: {str(e)}")
            return None


# -------------------- Análisis de riesgos --------------------
def analizar_riesgos_dorks(resultados: list, client: DeepSeekClient) -> Optional[List[Dict]]:
    """Analiza resultados y devuelve JSON estructurado con:
    [
        {
            "nrodork": int,
            "enlace": str,
            "clasificacion": "Alto/Medio/Bajo",
            "explicacion": str,
            "mitigacion": str
        }
    ]
    """
    if not resultados:
        logging.warning("Lista de resultados vacía recibida para análisis")
        return None

    # Preparar datos para el prompt
    resultados_texto = "\n".join(
        f"Dork {i+1}: {r.get('Titulo', 'Sin título')} - Enlace: {r.get('Enlace', 'URL no disponible')}"
        for i, r in enumerate(resultados)
    )

    prompt = f"""
Como experto en seguridad informática, analiza estos resultados de búsqueda (dorks) 
y devuelve EXCLUSIVAMENTE un JSON con el siguiente formato para cada elemento:

{{
    "analisis": [
        {{
            "nrodork": 1,
            "enlace": "url_completa",
            "clasificacion": "Alto/Medio/Bajo",
            "explicacion": "1-2 oraciones técnicas",
            "mitigacion": "Acciones concretas (máx 2 puntos)"
        }}
    ]
}}

Criterios de clasificación:
- Alto: Credenciales, archivos .sql/.env, paneles de administración expuestos
- Medio: Directorios listables, información técnica sensible
- Bajo: Contenido genérico sin datos sensibles

Datos a analizar:
{resultados_texto}

Importante:
- Solo incluye el JSON válido, sin texto adicional
- Usa comillas dobles para las propiedades
- Mantén el formato exacto solicitado
"""

    respuesta = client.analyze_content(prompt)
    
    if not respuesta:
        return None

    if "```json" in respuesta:
        respuesta = respuesta.split("```json")[1].split("```")[0].strip()
        

    try:
        datos = json.loads(respuesta)
        return datos.get("analisis", [])
    except json.JSONDecodeError:
        logging.error("La IA no devolvió un JSON válido")
        return None

# -------------------- Función principal --------------------
def main_ia(resultados: list) -> List[Dict]:
    """Flujo principal que devuelve directamente el formato estructurado"""
    if not resultados:
        return []

    try:
        env_vars = load_env_variables()
        if not env_vars:
            return []

        client = DeepSeekClient(env_vars['deepseek_api_key'])
        analisis = analizar_riesgos_dorks(resultados, client)
        
        return analisis if analisis else []

    except Exception as e:
        logging.error(f"Error en main_ia: {str(e)}", exc_info=True)
        return []