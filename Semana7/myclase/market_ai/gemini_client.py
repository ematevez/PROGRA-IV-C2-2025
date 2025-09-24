import os
import logging
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

def get_client():
    """
    Crea un cliente genai según si hay API key o se usa Vertex AI.
    """
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    use_vertex = os.environ.get("GOOGLE_GENAI_USE_VERTEXAI", "false").lower() in ("1","true","yes")
    
    if use_vertex:
        project = os.environ.get("GOOGLE_CLOUD_PROJECT")
        location = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
        client = genai.Client(vertexai=True, project=project, location=location)
    else:
        if not api_key:
            raise ValueError("GEMINI_API_KEY no encontrada en variables de entorno")
        client = genai.Client(api_key=api_key)
    return client

_client = None
def client():
    global _client
    if _client is None:
        _client = get_client()
    return _client

# Generación de texto corregida
def generate_text(prompt, model="gemini-1.5-flash", max_output_tokens=300):
    c = client()
    try:
        # Configuración correcta para la nueva API
        config = types.GenerateContentConfig(
            max_output_tokens=max_output_tokens,
            temperature=0.7
        )
        
        # Llamada corregida
        response = c.models.generate_content(
            model=model, 
            contents=prompt,
            config=config
        )
        
        # Extraer el texto de la respuesta
        if hasattr(response, 'text'):
            return response.text
        elif hasattr(response, 'candidates') and response.candidates:
            return response.candidates[0].content.parts[0].text
        else:
            return str(response)
            
    except Exception as e:
        logger.exception("Error al llamar a Gemini generate_content")
        return f"Error al generar texto: {e}"

# Generar embedding corregido
def embed_text(text, model="text-embedding-004"):
    c = client()
    try:
        response = c.models.embed_content(
            model=model, 
            contents=text
        )
        
        if hasattr(response, 'embeddings'):
            embeddings = response.embeddings
            if isinstance(embeddings, list) and len(embeddings) > 0:
                return embeddings[0].values if hasattr(embeddings[0], 'values') else embeddings[0]
            return embeddings
        return response
        
    except Exception as e:
        logger.exception("Error al generar embedding")
        return None