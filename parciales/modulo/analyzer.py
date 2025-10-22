import os
from datetime import datetime
import ollama
from utils import timestamp

class AnalizadorAutonomo:
    def __init__(self, modelos_base):
        self.modelos = modelos_base

    def analizar_codigo(self, filepath, max_preview_chars=3000):
        """
        Pide a un modelo una mejora específica para el código.
        Devuelve dict {'mejora':..., 'razon':...} o None.
        """
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                codigo = f.read()
        except Exception as e:
            return None

        num_lineas = codigo.count("\n") + 1
        num_funcs = codigo.count("def ")
        num_clases = codigo.count("class ")

        prompt = f"""Eres un asistente que sugiere UNA mejora técnica, específica y no trivial para el siguiente código. No sugieras documentación. Formato de salida EXACTO:

MEJORA: [frase breve]
RAZÓN: [una frase justificando la mejora]

Contexto:
- lineas: {num_lineas}
- funciones: {num_funcs}
- clases: {num_clases}

Código (preview):
{codigo[:max_preview_chars]}

Responde solo con las dos líneas pedidas.
"""
        try:
            modelo = self.modelos[0] if self.modelos else None
            if modelo:
                resp = ollama.chat(model=modelo, messages=[{"role":"user","content":prompt}])
                contenido = resp.get("message",{}).get("content","").strip()
            else:
                return None

            if "MEJORA:" in contenido and "RAZÓN:" in contenido:
                mejora = contenido.split("MEJORA:")[1].split("RAZÓN:")[0].strip()
                razon = contenido.split("RAZÓN:")[1].strip()
                return {"mejora": mejora, "razon": razon, "timestamp": datetime.now().isoformat()}
            # fallback lines
            lines = [l.strip() for l in contenido.splitlines() if l.strip()]
            if len(lines) >= 2:
                return {"mejora": lines[0], "razon": lines[1], "timestamp": datetime.now().isoformat()}
        except Exception as e:
            return None
        return None

    def generar_idea_emergente(self):
        prompt = "Genera UNA idea de mejora innovadora para un agente de auto-mejora de código. Responde solo una frase."
        try:
            modelo = self.modelos[1] if len(self.modelos)>1 else self.modelos[0]
            resp = ollama.chat(model=modelo, messages=[{"role":"user","content":prompt}])
            idea = resp.get("message",{}).get("content","").strip().splitlines()[0]
            return idea[:200]
        except:
            return None
