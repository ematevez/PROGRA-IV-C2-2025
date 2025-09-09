import pyttsx3

# Inicializar motor de voz
engine = pyttsx3.init()

# Texto a leer
texto = ""

# Hablar
engine.say(texto)
engine.runAndWait()
