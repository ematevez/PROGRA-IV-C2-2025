import time
from self_improver import SelfImprover

class Core:
    def __init__(self):
        self.config = {
            "modelos": ["gemma3:4b", "qwen2.5:3b"]
        }

if __name__ == "__main__":
    core = Core()
    improver = SelfImprover(core)

    print("🧠 Sistema autoevolutivo iniciado. Presiona Ctrl+C para detenerlo.\n")

    while True:
        try:
            print("=" * 60)
            print(f"⏰ Nuevo ciclo de mejora - {time.strftime('%Y-%m-%d %H:%M:%S')}")
            improver.generate_new_code()
        except Exception as e:
            print(f"⚠️ Error en el ciclo: {e}")
        time.sleep(120)
