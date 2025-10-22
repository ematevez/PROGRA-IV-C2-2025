import os
import json
from utils import read_json, write_json

class EvaluadorModelos:
    def __init__(self, archivo_metricas, modelos_iniciales):
        self.archivo = archivo_metricas
        self.metricas = read_json(self.archivo, default=None) or self._init_metricas(modelos_iniciales)

    def _init_metricas(self, modelos):
        template = {}
        for m in modelos:
            template[m] = {"usos": 0, "exitos": 0, "fallos":0, "tiempo_promedio":0.0, "calidad_promedio":0.0}
        return template

    def guardar(self):
        write_json(self.archivo, self.metricas)

    def registrar_uso(self, modelo, tiempo, exito, calidad=None):
        if modelo not in self.metricas:
            self.metricas[modelo] = {"usos":0, "exitos":0, "fallos":0, "tiempo_promedio":0.0, "calidad_promedio":0.0}
        m = self.metricas[modelo]
        m["usos"] += 1
        if exito:
            m["exitos"] += 1
            if calidad is not None:
                prev_exitos = m["exitos"] - 1
                if prev_exitos <= 0:
                    m["calidad_promedio"] = calidad
                else:
                    m["calidad_promedio"] = (m["calidad_promedio"] * prev_exitos + calidad) / m["exitos"]
        else:
            m["fallos"] += 1
        # update average time
        m["tiempo_promedio"] = (m["tiempo_promedio"] * (m["usos"]-1) + tiempo) / m["usos"]
        self.guardar()

    def obtener_mejor_modelo(self):
        mejor = None
        mejor_score = -1
        for modelo, s in self.metricas.items():
            if s["usos"] == 0:
                continue
            tasa = s["exitos"] / s["usos"] if s["usos"]>0 else 0
            calidad = (s["calidad_promedio"]/10) if s["calidad_promedio"] else 0
            velocidad = 1.0 / (s["tiempo_promedio"] + 1.0)
            score = tasa*0.5 + calidad*0.3 + velocidad*0.2
            if score > mejor_score:
                mejor_score = score
                mejor = modelo
        return mejor
