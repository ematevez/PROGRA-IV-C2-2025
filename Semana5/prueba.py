import pywhatkit as kit
import pyautogui
import time
import random

# Mensaje a enviar
mensaje = "Espero la respuesta o la transferencia"

# Lista de chistes
chistes = [
    "¿Por qué los pájaros no usan Facebook? Porque ya tienen Twitter.",
    "¿Qué hace una abeja en el gimnasio? ¡Zum-ba!",
    "¿Cómo se despiden los químicos? Ácido un placer.",
    "¿Qué le dice un jardinero a otro? ¡Disfrutemos mientras podamos!",
    "¿Por qué el libro de matemáticas se deprimió? Porque tenía demasiados problemas.",
    "¿Cómo se dice pañuelo en japonés? Saka-moko.",
    "¿Qué le dijo un pez a otro pez? Nada.",
    "¿Por qué los esqueletos no pelean entre ellos? Porque no tienen agallas.",
    "¿Qué hace una abeja en una cafetería? ¡Tomar un café con miel!",
    "¿Qué le dice una iguana a su hermana gemela? Iguanita.",
    "¿Qué hace una abeja en la disco? ¡Zum-ba!",
    "¿Qué le dice una iguana a otra? Somos iguanitas.",
    "¿Por qué las focas miran siempre hacia arriba? ¡Porque ahí están los focos!",
    "¿Por qué el libro de historia estaba deprimido? ¡Porque tenía demasiados conflictos!",
    "¿Cuál es el colmo de Aladdín? Tener mal genio.",
    "¿Qué hace una abeja en el gimnasio? ¡Zum-ba!",
    "¿Por qué los pájaros no usan Facebook? Porque ya tienen Twitter.",
    "¿Qué hace una abeja en la cafetería? ¡Tomar un café con miel!",
    "¿Qué le dice una iguana a su hermana gemela? Iguanita.",
    "¿Qué le dijo un jardinero a otro? ¡Disfrutemos mientras podamos!",
    "¿Cómo se despiden los químicos? Ácido un placer.",
    "¿Qué hace una abeja en el gimnasio? ¡Zum-ba!",
    "¿Por qué los pájaros no usan Facebook? Porque ya tienen Twitter.",
    "¿Qué hace una abeja en la disco? ¡Zum-ba!",
    "¿Por qué los esqueletos no pelean entre ellos? Porque no tienen agallas.",
    "¿Qué le dice una iguana a otra? Somos iguanitas.",
    "¿Por qué las focas miran siempre hacia arriba? ¡Porque ahí están los focos!",
    "¿Por qué el libro de historia estaba deprimido? ¡Porque tenía demasiados conflictos!",
    "¿Cuál es el colmo de Aladdín? Tener mal genio."
]

# Números de teléfono de los receptores
phone_numbers = ["+5491123716802", "+5491141981322", "+5491123823766" ]

# Tiempo total en minutos
tiempo_total = 60
# Intervalo de envío en minutos
intervalo = 1
# Número de veces que se enviará el mensaje
veces_a_enviar = tiempo_total // intervalo

# Enviar mensaje cada 1 minutos durante 1 hora
for i in range(veces_a_enviar):
    # Seleccionar un chiste aleatorio
    chiste = random.choice(chistes)
    # Combinar el mensaje principal con el chiste
    mensaje_a_enviar = f"{mensaje} - {chiste}"
    
    # Seleccionar el número de teléfono alternando entre los disponibles
    phone_number = phone_numbers[i % len(phone_numbers)]
    
    # Enviar el mensaje usando pywhatkit
    kit.sendwhatmsg_instantly(phone_number, mensaje_a_enviar)
    # Esperar unos segundos para que el mensaje se escriba en el cuadro de texto
    time.sleep(10)
    # Presionar Enter para enviar el mensaje
    pyautogui.press('enter')
    print(f"Mensaje enviado a {phone_number}: {mensaje_a_enviar}")
    # Esperar 3 minutos antes de enviar el siguiente mensaje
    time.sleep(intervalo * 60)
