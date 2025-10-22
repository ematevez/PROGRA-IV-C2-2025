import os
import subprocess
from utils import run_subprocess
from dataset_manager import DatasetManager

class Entrenador:
    def __init__(self, modelos_base, modelo_entrenado, archivo_dataset, modelfile_path="Modelfile"):
        self.modelos_base = modelos_base
        self.modelo_entrenado = modelo_entrenado
        self.archivo_dataset = archivo_dataset
        self.modelfile_path = modelfile_path

    def generar_modelfile(self, buenos_ejemplos):
        if not buenos_ejemplos:
            return None
        content = f"FROM {self.modelos_base[0]}\n\nPARAMETER temperature 0.7\nPARAMETER top_p 0.9\n\nSYSTEM Eres un modelo personalizado.\n\n"
        for i, e in enumerate(buenos_ejemplos[:10]):
            prompt = e.get("prompt","")[:200].replace("```","")
            completion = e.get("completion","")[:200].replace("```","")
            content += f"""# Ejemplo {i+1}
TEMPLATE \"\"\"Usuario: {prompt}
Asistente: {completion}\"\"\"\n\n"""
        return content

    def create_modelfile_and_train(self, dataset_manager):
        buenos = dataset_manager.buenos_ejemplos()
        if len(dataset_manager.datos) < 3:
            return False, "No hay suficientes datos"
        modelfile = self.generar_modelfile(buenos)
        if not modelfile:
            return False, "No pudo generarse modelfile"
        with open(self.modelfile_path, "w", encoding="utf-8") as f:
            f.write(modelfile)
        # Ejecutar ollama create
        cmd = ["ollama", "create", self.modelo_entrenado, "-f", self.modelfile_path]
        code, out, err = run_subprocess(cmd, timeout=600)
        if code == 0:
            return True, out
        else:
            return False, err
