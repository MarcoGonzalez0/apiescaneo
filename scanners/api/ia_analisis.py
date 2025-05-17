import os
import json
import logging
import requests
from dotenv import load_dotenv
from typing import Optional, Dict, List

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
def analizar_riesgos_dorks(resultados: list, client: DeepSeekClient) -> Optional[str]:
    """Analiza los resultados de búsqueda usando DeepSeek"""
    if not resultados:
        logging.warning("Lista de resultados vacía recibida para análisis")
        return None

    resultados_texto = "\n".join([f"{i+1}. {r}" for i, r in enumerate(resultados)])

    prompt = f"""
Como experto en seguridad informática, analiza los siguientes resultados de búsqueda (dorks) 
que podrían indicar filtraciones o exposiciones de datos sensibles.

Para cada entrada:
1. Clasifica el nivel de riesgo (bajo, medio, alto)
2. Explica brevemente tu evaluación
3. Proporciona recomendaciones de acción

Resultados a analizar:
{resultados_texto}

Formato de respuesta esperado:
[Ítem N°] [Tipo de riesgo] - [Breve explicación]
[Recomendación específica]
[Línea separadora]
"""

    return client.analyze_content(prompt)

# -------------------- Gestión de reportes --------------------
def guardar_resumen_json(resumen: str, nombre_archivo: str) -> Optional[str]:
    """Guarda el resumen de análisis en formato JSON"""
    try:
        os.makedirs("reportes", exist_ok=True)
        ruta = os.path.join("reportes", f"{nombre_archivo}.json")
        
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump({
                "fecha_analisis": str(datetime.now()),
                "resumen": resumen
            }, f, ensure_ascii=False, indent=4)
        
        logging.info(f"Reporte guardado en: {ruta}")
        return ruta
    except Exception as e:
        logging.error(f"Error al guardar el reporte: {str(e)}")
        return None

# -------------------- Función principal --------------------
def main_ia(resultados: list) -> List[str]:
    """Flujo principal de análisis de riesgos"""
    if not resultados:
        logging.warning("No se recibieron resultados para analizar")
        return []

    # Cargar configuración
    env_vars = load_env_variables()
    if not env_vars:
        return []

    # Inicializar cliente DeepSeek
    client = DeepSeekClient(env_vars['deepseek_api_key'])

    # Realizar análisis
    resumen = analizar_riesgos_dorks(resultados, client)
    if not resumen:
        logging.error("No se pudo obtener el análisis de riesgos")
        return []

    # Guardar resultados
    archivo = guardar_resumen_json(resumen, "resumen_dorks")
    return [archivo] if archivo else []

# Ejemplo de uso
if __name__ == "__main__":
    # Datos de ejemplo
    resultados_ejemplo = [
        "sitio.com/admin/config.php expuesto",
        "intranet.corporacion.com sin autenticación",
        "github.com/empleado/repo con credenciales en código"
    ]
    
    # Ejecutar análisis
    reportes_generados = main_ia(resultados_ejemplo)
    print(f"Reportes generados: {reportes_generados}")