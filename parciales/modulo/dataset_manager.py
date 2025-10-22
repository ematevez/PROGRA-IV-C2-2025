import os
import json
from datetime import datetime
from utils import ensure_dir

class DatasetManager:
    def __init__(self, archivo):
        self.archivo = archivo
        ensure_dir(os.path.dirname(self.archivo) or ".")
        self.datos = self.cargar_dataset()

    def cargar_dataset(self):
        if os.path.exists(self.archivo):
            datos = []
            with open(self.archivo, "r", encoding="utf-8") as f:
                for linea in f:
                    linea = linea.strip()
                    if not linea:
                        continue
                    try:
                        datos.append(json.loads(linea))
                    except:
                        continue
            return datos
        return []

    def agregar_ejemplo(self, instruccion, codigo_entrada, codigo_salida, modelo_usado, calidad):
        ejemplo = {
            "timestamp": datetime.now().isoformat(),
            "prompt": instruccion,
            "input": codigo_entrada,
            "completion": codigo_salida,
            "modelo": modelo_usado,
            "calidad": calidad,
            "len_input": len(codigo_entrada) if codigo_entrada else 0,
            "len_output": len(codigo_salida) if codigo_salida else 0
        }
        self.datos.append(ejemplo)
        with open(self.archivo, "a", encoding="utf-8") as f:
            f.write(json.dumps(ejemplo, ensure_ascii=False) + "\n")
        return ejemplo

    def conteo(self):
        return len(self.datos)

    def buenos_ejemplos(self, min_calidad=7, top_n=10):
        buenos = [d for d in self.datos if d.get("calidad",0) >= min_calidad]
        if len(buenos) < 3:
            buenos = sorted(self.datos, key=lambda x: x.get("calidad",0), reverse=True)[:top_n]
        return buenos
