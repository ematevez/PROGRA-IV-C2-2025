import ollama
import os
import sys
import time
import json
import threading
import subprocess
from datetime import datetime

# ============ CONFIGURACIÓN ============
MODELOS = ["gemma3:4b", "qwen2.5:3b"]
ARCHIVO_YO_MISMO = __file__  # Este mismo archivo
ARCHIVO_CONOCIMIENTO = "conocimiento.json"
TIEMPO_AUTO_MEJORA = 180  # 3 minutos sin usar

# Variables globales
ultima_actividad = time.time()
modo_aprendizaje = False

# ============ CLASE PRINCIPAL ============
class SistemaEvolutivo:
    """
    Sistema que se modifica a sí mismo y se reinicia
    """
    
    def __init__(self):
        self.version = "1.0"
        self.iteracion = self.cargar_iteracion()
        self.conocimiento = self.cargar_conocimiento()
        
    def cargar_iteracion(self):
        """Lee qué iteración es esta del propio código"""
        try:
            with open(__file__, 'r', encoding='utf-8') as f:
                primera_linea = f.readline()
                if '# ITERACION:' in primera_linea:
                    return int(primera_linea.split(':')[1].strip())
        except:
            pass
        return 0
    
    def cargar_conocimiento(self):
        if os.path.exists(ARCHIVO_CONOCIMIENTO):
            with open(ARCHIVO_CONOCIMIENTO, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "mejoras_aplicadas": [],
            "preferencias": [],
            "patrones_exitosos": []
        }
    
    def guardar_conocimiento(self):
        with open(ARCHIVO_CONOCIMIENTO, 'w', encoding='utf-8') as f:
            json.dump(self.conocimiento, f, indent=2, ensure_ascii=False)
    
    def mostrar_info(self):
        print("\n" + "="*60)
        print(f"🧬 SISTEMA AUTO-EVOLUTIVO - Iteración {self.iteracion}")
        print("="*60)
        print(f"📦 Modelos: {', '.join(MODELOS)}")
        print(f"🧠 Mejoras aplicadas: {len(self.conocimiento['mejoras_aplicadas'])}")
        print("="*60)
        
        if self.conocimiento['mejoras_aplicadas']:
            print("\n📋 Últimas mejoras:")
            for mejora in self.conocimiento['mejoras_aplicadas'][-3:]:
                print(f"   • {mejora['descripcion']} ({mejora['timestamp'][:10]})")
        
        print("\n💬 Comandos:")
        print("   - Escribe qué funcionalidad agregar")
        print("   - 'info' = ver información del sistema")
        print("   - 'salir' = terminar")
        print("="*60)
    
    def pedir_mejora_multi_modelo(self, instruccion):
        """Usa múltiples modelos y elige el mejor"""
        
        # Leer código actual (este archivo)
        with open(__file__, 'r', encoding='utf-8') as f:
            codigo_actual = f.read()
        
        prompt = f"""Eres un programador experto. Este es un sistema que se modifica a sí mismo.

TAREA: Agrega esta funcionalidad: {instruccion}

REGLAS CRÍTICAS:
1. MANTÉN TODO el código existente
2. Agrega la funcionalidad en la clase SistemaEvolutivo
3. Si es una nueva característica, agrégala como método
4. Actualiza el método mostrar_info() si corresponde
5. El código DEBE ser Python válido
6. NO elimines las importaciones ni la estructura principal
7. Incrementa la versión si es un cambio importante

CÓDIGO ACTUAL:
{codigo_actual}

RESPONDE SOLO CON EL CÓDIGO COMPLETO MODIFICADO."""
        
        resultados = {}
        
        def consultar(modelo):
            try:
                print(f"   🤖 {modelo} trabajando...")
                resp = ollama.chat(model=modelo, messages=[{'role': 'user', 'content': prompt}])
                contenido = resp['message']['content']
                
                # Extraer código
                if '```python' in contenido:
                    inicio = contenido.find('```python') + 9
                    fin = contenido.find('```', inicio)
                    codigo = contenido[inicio:fin].strip()
                elif '```' in contenido:
                    inicio = contenido.find('```') + 3
                    fin = contenido.find('```', inicio)
                    codigo = contenido[inicio:fin].strip()
                else:
                    codigo = contenido.strip()
                
                resultados[modelo] = codigo
                print(f"   ✅ {modelo} completado")
            except Exception as e:
                print(f"   ❌ {modelo} falló: {e}")
                resultados[modelo] = None
        
        # Ejecutar en paralelo
        threads = []
        for modelo in MODELOS:
            t = threading.Thread(target=consultar, args=(modelo,))
            t.start()
            threads.append(t)
        
        for t in threads:
            t.join()
        
        # Elegir el mejor (el más largo y válido)
        mejor = None
        max_len = 0
        
        for modelo, codigo in resultados.items():
            if codigo and len(codigo) > max_len:
                try:
                    compile(codigo, '<string>', 'exec')
                    mejor = codigo
                    max_len = len(codigo)
                    print(f"   🏆 Mejor: {modelo} ({len(codigo)} chars)")
                except:
                    print(f"   ⚠️  {modelo} tiene errores de sintaxis")
        
        return mejor
    
    def auto_mejorarme(self, nuevo_codigo, descripcion):
        """Reescribe este archivo con el nuevo código y se reinicia"""
        
        # Guardar el nuevo código
        nueva_iteracion = self.iteracion + 1
        header = f"# ITERACION: {nueva_iteracion}\n"
        
        with open(__file__, 'w', encoding='utf-8') as f:
            f.write(header + nuevo_codigo)
        
        # Registrar en conocimiento
        self.conocimiento['mejoras_aplicadas'].append({
            'iteracion': nueva_iteracion,
            'descripcion': descripcion,
            'timestamp': datetime.now().isoformat()
        })
        self.guardar_conocimiento()
        
        print(f"\n✅ Sistema modificado - Iteración {nueva_iteracion}")
        print("🔄 Reiniciando en 2 segundos...")
        time.sleep(2)
        
        # Reiniciar este script
        os.execv(sys.executable, [sys.executable] + sys.argv)
    
    def ejecutar(self):
        self.mostrar_info()
        
        while True:
            print("\n" + "="*60)
            instruccion = input("👉 ¿Qué agregar? ").strip()
            
            if not instruccion:
                continue
            
            if instruccion.lower() in ['salir', 'exit', 'quit']:
                print("\n👋 ¡Hasta luego!")
                break
            
            if instruccion.lower() == 'info':
                self.mostrar_info()
                continue
            
            print(f"\n🔧 Generando mejora...")
            nuevo_codigo = self.pedir_mejora_multi_modelo(instruccion)
            
            if nuevo_codigo:
                print("✅ Código generado correctamente")
                
                respuesta = input("\n¿Aplicar mejora y reiniciar? (s/n): ").strip().lower()
                if respuesta == 's':
                    self.auto_mejorarme(nuevo_codigo, instruccion)
                else:
                    print("❌ Mejora descartada")
            else:
                print("❌ No se pudo generar código válido")

# ============ EJECUCIÓN ============
if __name__ == "__main__":
    sistema = SistemaEvolutivo()
    sistema.ejecutar()