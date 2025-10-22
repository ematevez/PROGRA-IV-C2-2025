import json, subprocess, random
from logger import Logger

class SelfImprover:
    def __init__(self, core):
        self.core = core
        self.logger = Logger()
    
    def get_prompt(self):
        # 1️⃣ Revisar si hay prompt manual
        try:
            with open("manual_prompt.txt", "r", encoding="utf-8") as f:
                prompt = f.read().strip()
            if prompt:
                # Limpiar el archivo para la próxima vez
                open("manual_prompt.txt", "w", encoding="utf-8").close()
                return prompt
        except FileNotFoundError:
            pass

        # 2️⃣ Si no hay prompt manual, usar uno aleatorio
        prompts = [
            "optimiza el manejo de memoria y procesos",
            "mejora la estabilidad del sistema de automejora",
            "refactoriza el código para hacerlo más legible y eficiente",
            "agrega verificación adicional antes de sobrescribirse"
        ]
        import random
        return random.choice(prompts)
    
    def generate_new_code(self):
        models = self.core.config["modelos"]
        base_code = open("core.py", "r", encoding="utf-8").read()
        prompts = [
            "optimiza el manejo de memoria y procesos",
            "mejora la estabilidad del sistema de automejora",
            "refactoriza el código para hacerlo más legible y eficiente",
            "agrega verificación adicional antes de sobrescribirse"
        ]
        # prompt = random.choice(prompts)
        prompt = self.get_prompt()

        self.logger.log(f"Usando prompt: {prompt}")

        mejor_codigo = None
        for model in models:
            try:
                output = subprocess.run(
                ["ollama", "run", model],
                input=f"Analiza y mejora este código Python:\n{base_code}\n{prompt}",
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace")

                if output.returncode == 0 and "class CoreAgent" in output.stdout:
                    mejor_codigo = output.stdout
                    self.logger.log(f"✅ {model} generó una versión válida.")
                    break
            except Exception as e:
                self.logger.log(f"Error con modelo {model}: {e}")

        if not mejor_codigo:
            self.logger.log("Ningún modelo generó código válido.")
        return mejor_codigo
