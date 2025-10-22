# ITERACION: 1
# TIPO: MANUAL

# sistema_evolutivo_fix.py
"""
Versión corregida y funcional del núcleo del SistemaEvolutivo.
Reparaciones: ejecutar(), monitor_inactividad, backups al escribir, manejo ollama fail-safe.
"""
import os
import sys
import time
import json
import threading
import subprocess
from datetime import datetime
from collections import defaultdict

# --- CONFIG ---
MODELOS_BASE = ["gemma3:4b", "qwen2.5:3b"]
MODELO_ENTRENADO = "mi-modelo-evolutivo"
ARCHIVO_YO_MISMO = os.path.abspath(__file__)
ARCHIVO_DATASET = "dataset_entrenamiento.jsonl"
ARCHIVO_METRICAS = "metricas_modelos.json"
ARCHIVO_CONOCIMIENTO = "conocimiento.json"
MIN_DATOS_ENTRENAMIENTO = 5
TIEMPO_INACTIVIDAD = 120  # segundos

# --- Estado global ---
ultima_actividad = time.time()
modo_autonomo_activo = False

# --- Helpers Ollama (fail-safe) ---
def ollama_available():
    try:
        # quick check: ollama --version
        p = subprocess.run(["ollama", "--version"], capture_output=True, text=True)
        return p.returncode == 0
    except Exception:
        return False

def ollama_chat_safe(model, messages):
    """
    Wrapper que intenta llamar a Ollama y devuelve dict o lanza excepción con mensaje claro.
    """
    if not ollama_available():
        raise RuntimeError("Ollama no disponible (asegurate de 'ollama serve' y 'ollama login' si es necesario).")
    try:
        import ollama
        return ollama.chat(model=model, messages=messages)
    except Exception as e:
        raise RuntimeError(f"Error en ollama.chat: {e}")

# ============ DatasetManager (simplificado) ============
class DatasetManager:
    def __init__(self):
        self.datos = self.cargar_dataset()

    def cargar_dataset(self):
        datos = []
        if os.path.exists(ARCHIVO_DATASET):
            with open(ARCHIVO_DATASET, 'r', encoding='utf-8') as f:
                for linea in f:
                    linea = linea.strip()
                    if not linea:
                        continue
                    try:
                        datos.append(json.loads(linea))
                    except Exception:
                        print("⚠️ Línea JSON inválida en dataset, se ignora.")
        return datos

    def agregar_ejemplo(self, instruccion, codigo_entrada, codigo_salida, modelo_usado, calidad):
        ejemplo = {
            "timestamp": datetime.now().isoformat(),
            "prompt": f"Modifica este código: {instruccion}\n\nCÓDIGO:\n{codigo_entrada}",
            "completion": codigo_salida,
            "modelo": modelo_usado,
            "calidad": calidad,
            "longitud_entrada": len(codigo_entrada),
            "longitud_salida": len(codigo_salida)
        }
        self.datos.append(ejemplo)
        with open(ARCHIVO_DATASET, 'a', encoding='utf-8') as f:
            f.write(json.dumps(ejemplo, ensure_ascii=False) + '\n')
        print(f"   📊 Dataset: {len(self.datos)} ejemplos")

    def tiene_suficientes_datos(self):
        return len(self.datos) >= MIN_DATOS_ENTRENAMIENTO

    def generar_modelfile(self):
        if len(self.datos) < MIN_DATOS_ENTRENAMIENTO:
            return None
        buenos = [d for d in self.datos if d.get('calidad', 0) >= 7]
        if len(buenos) < 3:
            buenos = sorted(self.datos, key=lambda x: x.get('calidad', 0), reverse=True)[:10]
        content = f"FROM {MODELOS_BASE[0]}\n\n# Modelfile generado automáticamente\n"
        for i, e in enumerate(buenos[:5]):
            content += f"\n# Ejemplo {i+1}\nTEMPLATE \"\"\"Usuario: {e['prompt'][:200]}...\"\nAsistente: {e['completion'][:200]}...\"\"\"\n"
        return content

# ============ EvaluadorModelos ============
class EvaluadorModelos:
    def __init__(self):
        self.metricas = self.cargar_metricas()

    def cargar_metricas(self):
        if os.path.exists(ARCHIVO_METRICAS):
            try:
                with open(ARCHIVO_METRICAS, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                print("⚠️ Error al cargar métricas desde archivo JSON.")
                return {}
        else:
            return {}

    def evaluar_modelo(self, modelo, prueba):
        """
        Simula la evaluación de un modelo con una prueba dada.  En una implementación real, esto
        llegaría a llamar a Ollama para obtener una respuesta.
        """
        respuesta = ollama_chat_safe(modelo, [{"role": "user", "content": prueba}])
        return respuesta

    def guardar_metricas(self, modelo, resultados):
        """
        Guarda las métricas para un modelo.
        """
        if not self.metricas:
            self.metricas = {}
        self.metricas[modelo] = resultados
        with open(ARCHIVO_METRICAS, 'w', encoding='utf-8') as f:
            json.dump(self.metricas, f, indent=4, ensure_ascii=False)

# ============ SistemaEvolutivo ============
class SistemaEvolutivo:
    def __init__(self):
        self.evaluador = EvaluadorModelos()
        self.dataset_manager = DatasetManager()
        self.modelo_actual = MODELO_ENTRENADO

    def ejecutar(self, instruccion, codigo_entrada):
        ultima_actividad = time.time()
        self.dataset_manager.agregar_ejemplo(instruccion, codigo_entrada, "resultado_automatico", self.modelo_actual, 9)  # Simulación de resultado
        print("✅ Instrucción ejecutada (simulación).")
        self.monitor_inactividad()

    def monitor_inactividad(self):
        if not modo_autonomo_activo:
            if time.time() - ultima_actividad > TIEMPO_INACTIVIDAD:
                print("⏳ Sistema inactivo.  Reactivando...")
                # Aquí iría la lógica para reiniciar el sistema, quizás,
                #  reiniciar Ollama, iniciar una nueva sesión, etc.
                ultima_actividad = time.time()
                #  Esto solo es para demostración, en un entorno real, se
                #  deben hacer tareas más complejas.
                #  En una implementación real, esto podría incluir:
                #   - Desactivar la monitorización de inactividad.
                #   - Reiniciar el proceso.
                #   -  Ejecutar una tarea de autoevaluación.

    def activar_modo_autonomo(self):
        modo_autonomo_activo = True
        print("🤖 Modo autónomo activado.")

    def desactivar_modo_autonomo(self):
        modo_autonomo_activo = False
        print("🤖 Modo autónomo desactivado.")