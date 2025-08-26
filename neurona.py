# import google.generativeai as genai
  

# genai.configure(api_key="")
# model = genai.GenerativeModel("gemini-2.0-flash").start_chat()


# print("Habla conmigo! (escribe 'salir' para terminar)")

# while True:
#     user_input = input("Tú: ")
#     if user_input.lower() == "salir":
#         print("¡Adiós!")
#         break
#     response = chat.send_message(user_input)
#     print("Gemini dice: ", response.text)
    
    
    
    
# import google.generativeai as genai

# # Configura tu API key
# genai.configure(api_key="")

# # Crear modelo
# model = genai.GenerativeModel("gemini-1.5-flash")

# # Crear la sesión de chat
# chat = model.start_chat()

# print("Habla conmigo! (escribe 'salir' para terminar)")

# while True:
#     user_input = input("Tú: ")
#     if user_input.lower() == "salir":
#         print("Adiós! 👋")
#         break
    
#     response = chat.send_message(user_input)
#     print("Bot:", response.text)



# import os
# import subprocess
# import google.generativeai as genai

# # Configuración de Gemini
# genai.configure(api_key="")

# def generar_codigo(prompt, filename="script_generado.py"):
#     """Genera código con Gemini y lo guarda en un archivo .py"""
#     model = genai.GenerativeModel("gemini-1.5-flash")
#     response = model.generate_content(f"Escribe un script en Python que haga lo siguiente:\n{prompt}")

#     codigo = response.text
#     with open(filename, "w", encoding="utf-8") as f:
#         f.write(codigo)

#     print(f"\n✅ Código generado en {filename}\n")
#     return filename

# def ejecutar_script(filename):
#     """Ejecuta un script en Python"""
#     print(f"\n▶ Ejecutando {filename}...\n")
#     subprocess.run(["python", filename])

# def menu():
#     while True:
#         print("\n===== MENÚ =====")
#         print("1. Generar nuevo script con IA")
#         print("2. Ejecutar último script")
#         print("3. Modificar script con IA")
#         print("4. Salir")
        
#         opcion = input("Elige una opción: ")

#         if opcion == "1":
#             prompt = input("¿Qué querés que haga el nuevo script?: ")
#             global ultimo_archivo
#             ultimo_archivo = generar_codigo(prompt)
        
#         elif opcion == "2":
#             if 'ultimo_archivo' in globals():
#                 ejecutar_script(ultimo_archivo)
#             else:
#                 print("⚠ No hay script generado aún.")
        
#         elif opcion == "3":
#             if 'ultimo_archivo' in globals():
#                 prompt = input("¿Qué querés agregar o cambiar en el script?: ")
#                 generar_codigo(prompt, ultimo_archivo)  # reescribe el archivo existente
#                 print("✅ Script modificado.")
#             else:
#                 print("⚠ No hay script para modificar.")
        
#         elif opcion == "4":
#             print("👋 Saliendo...")
#             break
#         else:
#             print("Opción inválida.")

# if __name__ == "__main__":
#     menu()

import os
import google.generativeai as genai

# Configura tu API key de Google AI Studio
genai.configure(api_key="")

SCRIPT_NAME = "script_generado.py"
 #Arreglas esto que no borra las 2 primeras lineas y la ultima==============================0000
def limpiar_script():
    """Elimina líneas problemáticas del script."""
    if not os.path.exists(SCRIPT_NAME):
        print("No existe el script todavía.")
        return

    with open(SCRIPT_NAME, "r", encoding="utf-8") as f:
        lineas = f.readlines()

    # Filtramos líneas que contengan palabras clave de error
    lineas_limpias = [linea for linea in lineas if "COMO HAGO" not in linea]

    with open(SCRIPT_NAME, "w", encoding="utf-8") as f:
        f.writelines(lineas_limpias)

    print("Script limpiado!")
# ===============================================================================================
def correr_script():
    """Ejecuta el script generado."""
    if not os.path.exists(SCRIPT_NAME):
        print("No existe el script para ejecutar.")
        return
    os.system(f"python {SCRIPT_NAME}")

def generar_codigo(prompt):
    """Usa Gemini para generar o modificar código Python."""
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    codigo = response.text

    with open(SCRIPT_NAME, "w", encoding="utf-8") as f:
        f.write(codigo)

    print("Código generado y guardado en", SCRIPT_NAME)

def modificar_codigo(prompt):
    """Usa Gemini para modificar el código existente según prompt."""
    if not os.path.exists(SCRIPT_NAME):
        print("No existe el script para modificar.")
        return

    with open(SCRIPT_NAME, "r", encoding="utf-8") as f:
        codigo_actual = f.read()

    model = genai.GenerativeModel("gemini-1.5-flash")
    full_prompt = f"Modifica el siguiente código según estas instrucciones: {prompt}\n\nCódigo actual:\n{codigo_actual}"
    response = model.generate_content(full_prompt)
    codigo_modificado = response.text

    with open(SCRIPT_NAME, "w", encoding="utf-8") as f:
        f.write(codigo_modificado)

    print("Código modificado y guardado en", SCRIPT_NAME)

if __name__ == "__main__":
    while True:
        opcion = input("\nMenú:\n1) Generar nuevo script\n2) Modificar script existente\n3) Limpiar script\n4) Ejecutar script\n5) Salir\nElige: ")
        
        if opcion == "1":
            prompt = input("Describe qué quieres que haga el script: ")
            generar_codigo("Haceme en python lo que dice a continuacion " + prompt + " y asegurate que el codigo no tenga ningun texto solo listo para ejecutar")
        elif opcion == "2":
            prompt = input("Describe los cambios que quieres aplicar al script: ")
            modificar_codigo(prompt)
        elif opcion == "3":
            limpiar_script()
        elif opcion == "4":
            correr_script()
        elif opcion == "5":
            print("¡Adiós!")
            break
        else:
            print("Opción inválida.")
