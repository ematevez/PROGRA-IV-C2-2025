import json, subprocess, random, difflib, shutil, time, os, re
from logger import Logger

class SelfImprover:
    def __init__(self, core):
        self.core = core
        self.logger = Logger()


    def get_prompt(self):
        """Lee un prompt manual o usa uno aleatorio."""
        try:
            with open("manual_prompt.txt", "r", encoding="utf-8") as f:
                prompt = f.read().strip()
            if prompt:
                open("manual_prompt.txt", "w", encoding="utf-8").close()
                return prompt
        except FileNotFoundError:
            pass

        prompts = [
            "optimiza el manejo de memoria y procesos",
            "mejora la estabilidad del sistema de automejora",
            "refactoriza el código para hacerlo más legible y eficiente",
            "agrega verificación adicional antes de sobrescribirse"
        ]
        return random.choice(prompts)

    def mostrar_diferencias(self, viejo, nuevo):
        """Muestra las diferencias entre versiones."""
        diff = difflib.unified_diff(
            viejo.splitlines(), nuevo.splitlines(),
            fromfile='core.py (actual)',
            tofile='core_temp.py (nuevo)',
            lineterm=''
        )
        print("\n".join(diff))

    def backup_codigo(self):
        """Crea una copia de seguridad antes de sobrescribir."""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        shutil.copy("core.py", f"core_backup_{timestamp}.py")

    def limpiar_salida(self, texto):
        """Elimina comentarios, formato markdown y deja solo el código."""
        texto = re.sub(r"^```(?:python)?", "", texto, flags=re.MULTILINE)
        texto = re.sub(r"```$", "", texto, flags=re.MULTILINE)
        texto = re.sub(r"^#.*$", "", texto, flags=re.MULTILINE)
        texto = texto.strip()
        return texto

    def probar_core(self, ruta):
        """Ejecuta el nuevo core y devuelve True si pasa las pruebas."""
        try:
            result = subprocess.run(["python", ruta], capture_output=True, text=True, timeout=10)
            print(result.stdout)
            if "Todas las pruebas pasaron correctamente" in result.stdout:
                return True
            else:
                print(result.stderr)
                return False
        except Exception as e:
            self.logger.log(f"Error probando {ruta}: {e}")
            return False

    def generate_new_code(self):
        """Genera, evalúa y aplica una nueva versión de core.py."""
        base_code = open("core.py", "r", encoding="utf-8").read()
        prompt = self.get_prompt()
        self.logger.log(f"🤖 Usando prompt: {prompt}")

        mejor_codigo = None

        # Tomamos el último modelo de la lista configurada
        modelos = self.core.config.get("modelos", [])
        if not modelos:
            self.logger.log("⚠️ No hay modelos configurados en core.config['modelos'].")
            return
        modelo = modelos[-1]
        self.logger.log(f"🚀 Usando el modelo más reciente: {modelo}")

        try:
            output = subprocess.run(
                ["ollama", "run", modelo],
                input=f"Analiza y mejora este código Python y devuelve SOLO el código funcional, sin comentarios ni explicaciones:\n\n{base_code}\n\nInstrucción: {prompt}",
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace"
            )

            if output.returncode == 0:
                candidato = self.limpiar_salida(output.stdout)
                if "class CoreAgent" in candidato:
                    mejor_codigo = candidato
                    self.logger.log("✅ Código generado correctamente por el modelo.")
                else:
                    self.logger.log("❌ El modelo no generó una clase CoreAgent válida.")
            else:
                self.logger.log(f"⚠️ Error de modelo ({modelo}): {output.stderr}")
        except Exception as e:
            self.logger.log(f"Error ejecutando modelo {modelo}: {e}")
            return

        if not mejor_codigo:
            self.logger.log("❌ No se pudo obtener un nuevo código válido.")
            return

        # Guardar el nuevo código temporalmente
        with open("core_temp.py", "w", encoding="utf-8") as f:
            f.write(mejor_codigo)

        # Mostrar diferencias
        self.mostrar_diferencias(base_code, mejor_codigo)

        # Probar el nuevo código
        if self.probar_core("core_temp.py"):
            self.backup_codigo()
            shutil.move("core_temp.py", "core.py")
            self.logger.log("✅ Nuevo core aplicado con éxito.")
        else:
            os.remove("core_temp.py")
            self.logger.log("❌ Nuevo core rechazado por fallar las pruebas.")
