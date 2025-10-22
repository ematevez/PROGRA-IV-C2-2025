# ITERACION: 1
# TIPO: AUTÓNOMA
import threading
import time
from datetime import datetime

global modo_autonomo_activo, ultima_actividad, TIEMPO_INACTIVIDAD

TIEMPO_INACTIVIDAD = 60 * 5  # 5 minutos de inatividade para entrar em modo autônomo
ultima_actividade = time.time()

modo_autonomo_activo = False

class SistemaEvolutivo:
    def __init__(self):
        with open(__file__, 'r', encoding='utf-8') as f:
            self.codigo_anterior = f.read()
    
    def mostrar_info(self):
        print("\n" + "="*70)
        print("🤖 MODO AUTÓNOMO ACTIVADO")
        print("="*70)
        print("El sistema se auto-análiza e melhora sem guias...")
        print("Presiona ENTER para retomar control")
        print("="*70)
    
    def analisar_codigo_propio(self):
        return {'mejora': 'Implementação automática de novas funcionalidades', 'razao': 'Melhoria constante do código'}
    
    def gerar_mejora_emergente(self):
        return "Gerar nova ideia emergente"
    
    def aplicar_mejora(self, novo_codigo, descripcion, modelo_usado, tempo_execucao, es_autonoma=False):
        with open(__file__, 'r', encoding='utf-8') as f:
            codigo_anterior = f.read()
        
        if not es_autonoma:
            print("\nQualidade da melhoria? (1-10)")
            try:
                qualidade = int(input("👉 Qualidade: ").strip())
                qualidade = max(1, min(10, qualidade))
            except:
                qualidade = 5
        else:
            qualidade = 7
        
        self.dataset.adicionar_exemplo(descrição, codigo_anterior, novo_codigo, modelo_usado, qualidade)
        self.evaluador.registrar_uso(modelo_usado, tempo_execucao, True, qualidade)
        
        nova_iteração = self.iteração + 1
        tipo = "AUTÓNOMA" if es_autonoma else "MANUAL"
        header = f"# ITERAÇÃO: {nova_iteração}\n# TIPO: {tipo}\n"
        
        with open(__file__, 'w', encoding='utf-8') as f:
            f.write(header + novo_codigo)
        
        mejora_info = {
            'iteração': nova_iteração,
            'descrição': descrição,
            'modelo': modelo_usado,
            'calidade': qualidade,
            'timestamp': datetime.now().isoformat(),
            'autônoma': es_autonoma
        }
        
        if es_autonoma:
            if 'mejoras_autônomas' not in self.conhecimento:
                self.conhecimento['mejoras_autônomas'] = []
            self.conhecimento['mejoras_autônomas'].append(mejora_info)
        else:
            self.conhecimento['mejoras'].append(mejora_info)
        
        self.guardar_conhecimento()
        
        print(f"\n✅ Melhoria {tipo.lower()} aplicada - Iteração {nova_iteração}")
    
    def modo_autônomo(self):
        global modo_autonomo_activo
        self.mostrar_info()
        
        print("\n🔍 Fase 1: Auto-análise...")
        analisar = self.analizar_codigo_propio()
        
        if analisar:
            print(f"\n💡 Análise concluída:")
            print(f"   Melhoria: {analisar['mejora']}")
            print(f"   Razão: {analisar['razao']}")
            
            if 'auto_analisa' not in self.conhecimento:
                self.conhecimento['auto_análises'] = []
            self.conhecimento['auto_análises'].append(analisar)
            self.guardar_conhecimento()
            
            instrucao = analisar['melhoria']
        else:
            print("\n🌟 Fase 2: Geração de nova ideia emergente...")
            instrucao = self.gerar_mejora_emergente()
            
            if not instrucao:
                print("   ⚠️ Não foi gerada melhoria autônoma")
                modo_autonomo_activo = False
                return
            
            print(f"   Nova ideia: {instrucao}")
        
        print(f"\n🔧 Fase 3: Implementação...")
        codigo, modelo, tempo_execucao = self.gerar_mejora_multi_modelos(instrucao)
        
        if codigo:
            print("✅ Código gerado")
            resp = input("\nDeseja aplicar e reiniciar? (s/n): ").strip().lower()
            if resp == 's':
                self.aplicar_mejora(codigo, instrução, modelo, tempo_execucao, es_autônoma=True)
        else:
            print("❌ Não foi possível gerar código")
        
        modo_autonomo_activo = False
    
    def monitor_inatividade(self):
        global ultima_atividade
        while True:
            time.sleep(10)
            inatividade = time.time() - ultima_atividade
            
            if inatividade >= TIEMPO_INATIVIDADE and not modo_autonomo_activo:
                try:
                    self.modo_autônomo()
                    ultima_atividade = time.time()
                except Exception as e:
                    print(f"\n⚠️ Erro no modo autônomo: {e}")
                    modo_autonomo_activo = False
    
    def executar(self):
        global ultima_atividade
        self.mostrar_info()
        
        monitor_thread = threading.Thread(target=self.monitor_inatividade, daemon=True)
        monitor_thread.start()
        
        while True:
            print("\n" + "="*70)
            
            try:
                cmd = input("👉 Comando: ").strip()
                ultima_atividade = time.time()
            except:
                continue
            
            if not cmd:
                continue
            
            if cmd.lower() in ['salir', 'exit', 'quit']:
                print("\n👋 Até logo!")
                break
            
            if cmd.lower() == 'entra':
                if self.entrenar():
                    self.conhecimento['entra'] += 1
                    self.guardar_conhecimento()
                continue
            
            if cmd.lower() == 'stats':
                self.mostrar_info()
                continue
            
            if cmd.lower() == 'ranking':
                self.evaluador.mostra_ranking()
                continue
            
            if cmd.lower() == 'auto':
                self.modo_autônomo()
                continue