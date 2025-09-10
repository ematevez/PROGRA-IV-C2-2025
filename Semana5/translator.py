#!/usr/bin/env python3
"""
Script de Texto a Voz y Voz a Texto
Autor: Asistente IA
Fecha: 2025

Funcionalidades:
- Convertir texto a voz (TTS)
- Convertir voz a texto (STT)
- Interfaz interactiva por consola
"""

import speech_recognition as sr
import pyttsx3
import sys
import threading
import time

class VoiceTextConverter:
    def __init__(self):
        """Inicializar el convertidor de voz y texto"""
        # Configurar texto a voz
        self.tts_engine = pyttsx3.init()
        self.configure_tts()
        
        # Configurar voz a texto
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Configurar micrófono
        self.configure_microphone()
        
    def configure_tts(self):
        """Configurar el motor de texto a voz"""
        try:
            # Obtener voces disponibles
            voices = self.tts_engine.getProperty('voices')
            
            # Buscar voz en español si está disponible
            spanish_voice = None
            for voice in voices:
                if 'spanish' in voice.name.lower() or 'es' in voice.id.lower():
                    spanish_voice = voice.id
                    break
            
            if spanish_voice:
                self.tts_engine.setProperty('voice', spanish_voice)
                print("✅ Voz en español configurada")
            else:
                print("⚠️ Voz en español no disponible, usando voz por defecto")
            
            # Configurar velocidad y volumen
            self.tts_engine.setProperty('rate', 180)  # Velocidad
            self.tts_engine.setProperty('volume', 0.8)  # Volumen
            
        except Exception as e:
            print(f"❌ Error configurando TTS: {e}")
    
    def configure_microphone(self):
        """Configurar y calibrar el micrófono"""
        try:
            print("🎤 Calibrando micrófono...")
            with self.microphone as source:
                # Ajustar para ruido ambiente
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            print("✅ Micrófono calibrado")
        except Exception as e:
            print(f"❌ Error configurando micrófono: {e}")
    
    def text_to_speech(self, text):
        """Convertir texto a voz"""
        try:
            print(f"🔊 Reproduciendo: {text}")
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
            return True
        except Exception as e:
            print(f"❌ Error en texto a voz: {e}")
            return False
    
    def speech_to_text(self, timeout=5, phrase_time_limit=10):
        """Convertir voz a texto"""
        try:
            print(f"🎤 Escuchando... (máximo {timeout}s para empezar, {phrase_time_limit}s total)")
            
            with self.microphone as source:
                # Escuchar audio
                audio = self.recognizer.listen(
                    source, 
                    timeout=timeout, 
                    phrase_time_limit=phrase_time_limit
                )
            
            print("🔄 Procesando audio...")
            
            # Reconocer usando Google Speech Recognition
            text = self.recognizer.recognize_google(audio, language='es-ES')
            print(f"✅ Texto reconocido: {text}")
            return text
            
        except sr.WaitTimeoutError:
            print("⏱️ Tiempo de espera agotado")
            return None
        except sr.UnknownValueError:
            print("❓ No se pudo entender el audio")
            return None
        except sr.RequestError as e:
            print(f"❌ Error del servicio de reconocimiento: {e}")
            return None
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
            return None
    
    def interactive_mode(self):
        """Modo interactivo para usar las funcionalidades"""
        print("\n" + "="*50)
        print("🎯 CONVERTIDOR DE VOZ Y TEXTO")
        print("="*50)
        
        while True:
            print("\n📋 OPCIONES:")
            print("1. 📝 Texto a Voz")
            print("2. 🎤 Voz a Texto")
            print("3. 🔄 Conversación (Voz a Texto y respuesta)")
            print("4. ⚙️ Configuraciones")
            print("5. ❌ Salir")
            
            try:
                choice = input("\n🔸 Selecciona una opción (1-5): ").strip()
                
                if choice == '1':
                    self.text_to_speech_interface()
                elif choice == '2':
                    self.speech_to_text_interface()
                elif choice == '3':
                    self.conversation_mode()
                elif choice == '4':
                    self.settings_menu()
                elif choice == '5':
                    print("👋 ¡Hasta luego!")
                    break
                else:
                    print("⚠️ Opción no válida")
                    
            except KeyboardInterrupt:
                print("\n👋 ¡Hasta luego!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def text_to_speech_interface(self):
        """Interfaz para texto a voz"""
        print("\n📝 TEXTO A VOZ")
        print("-" * 30)
        
        while True:
            text = input("🔸 Escribe el texto (o 'salir' para volver): ").strip()
            
            if text.lower() == 'salir':
                break
            elif text:
                self.text_to_speech(text)
            else:
                print("⚠️ Por favor ingresa algún texto")
    
    def speech_to_text_interface(self):
        """Interfaz para voz a texto"""
        print("\n🎤 VOZ A TEXTO")
        print("-" * 30)
        
        while True:
            input("🔸 Presiona Enter para comenzar a grabar (o Ctrl+C para salir)...")
            
            try:
                result = self.speech_to_text()
                if result:
                    print(f"📄 Resultado: {result}")
                    
                    # Opción para guardar
                    save = input("💾 ¿Guardar en archivo? (s/n): ").lower()
                    if save == 's':
                        self.save_text_to_file(result)
                
            except KeyboardInterrupt:
                break
    
    def conversation_mode(self):
        """Modo conversación: escucha y responde"""
        print("\n🔄 MODO CONVERSACIÓN")
        print("-" * 30)
        print("💡 Di algo y el sistema repetirá lo que escuchó")
        
        while True:
            try:
                input("🔸 Presiona Enter para comenzar (o Ctrl+C para salir)...")
                
                # Escuchar
                text = self.speech_to_text()
                
                if text:
                    # Responder
                    response = f"Escuché: {text}"
                    print(f"🤖 Respuesta: {response}")
                    self.text_to_speech(response)
                
            except KeyboardInterrupt:
                break
    
    def settings_menu(self):
        """Menú de configuraciones"""
        print("\n⚙️ CONFIGURACIONES")
        print("-" * 30)
        
        print("1. 🔊 Ajustar velocidad de voz")
        print("2. 🔉 Ajustar volumen")
        print("3. 🎤 Probar micrófono")
        print("4. 🔙 Volver")
        
        choice = input("🔸 Selecciona opción: ").strip()
        
        if choice == '1':
            self.adjust_speech_rate()
        elif choice == '2':
            self.adjust_volume()
        elif choice == '3':
            self.test_microphone()
        elif choice == '4':
            return
    
    def adjust_speech_rate(self):
        """Ajustar velocidad de habla"""
        try:
            current_rate = self.tts_engine.getProperty('rate')
            print(f"Velocidad actual: {current_rate}")
            
            new_rate = input("Nueva velocidad (100-300, recomendado 180): ")
            new_rate = int(new_rate)
            
            if 50 <= new_rate <= 400:
                self.tts_engine.setProperty('rate', new_rate)
                self.text_to_speech("Velocidad ajustada correctamente")
            else:
                print("⚠️ Velocidad fuera de rango")
                
        except ValueError:
            print("⚠️ Por favor ingresa un número válido")
    
    def adjust_volume(self):
        """Ajustar volumen"""
        try:
            current_volume = self.tts_engine.getProperty('volume')
            print(f"Volumen actual: {current_volume}")
            
            new_volume = input("Nuevo volumen (0.0-1.0): ")
            new_volume = float(new_volume)
            
            if 0.0 <= new_volume <= 1.0:
                self.tts_engine.setProperty('volume', new_volume)
                self.text_to_speech("Volumen ajustado correctamente")
            else:
                print("⚠️ Volumen fuera de rango")
                
        except ValueError:
            print("⚠️ Por favor ingresa un número válido")
    
    def test_microphone(self):
        """Probar micrófono"""
        print("🎤 Prueba de micrófono - di 'hola mundo'")
        result = self.speech_to_text(timeout=10)
        
        if result:
            print("✅ Micrófono funcionando correctamente")
            self.text_to_speech("Micrófono funcionando correctamente")
        else:
            print("❌ Problema con el micrófono")
    
    def save_text_to_file(self, text):
        """Guardar texto en archivo"""
        try:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"transcripcion_{timestamp}.txt"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"Transcripción del {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("-" * 50 + "\n")
                f.write(text)
            
            print(f"💾 Guardado en: {filename}")
            
        except Exception as e:
            print(f"❌ Error guardando archivo: {e}")


def check_dependencies():
    """Verificar que las dependencias estén instaladas"""
    try:
        import speech_recognition
        import pyttsx3
        return True
    except ImportError as e:
        print("❌ Dependencias faltantes:")
        print("📦 Instala con: pip install speechrecognition pyttsx3 pyaudio")
        print(f"Error específico: {e}")
        return False


def main():
    """Función principal"""
    print("🚀 Iniciando Convertidor de Voz y Texto...")
    
    # Verificar dependencias
    if not check_dependencies():
        return
    
    try:
        # Crear instancia del convertidor
        converter = VoiceTextConverter()
        
        # Iniciar modo interactivo
        converter.interactive_mode()
        
    except Exception as e:
        print(f"❌ Error fatal: {e}")
        print("💡 Asegúrate de tener micrófono conectado y permisos de audio")


if __name__ == "__main__":
    main()