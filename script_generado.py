
import datetime

def signo_solar(fecha_nacimiento):
    mes, dia = fecha_nacimiento.month, fecha_nacimiento.day
    if (mes == 3 and dia >= 21) or (mes == 4 and dia <= 19):
        return "Aries"
    elif (mes == 4 and dia >= 20) or (mes == 5 and dia <= 20):
        return "Tauro"
    elif (mes == 5 and dia >= 21) or (mes == 6 and dia <= 20):
        return "Géminis"
    elif (mes == 6 and dia >= 21) or (mes == 7 and dia <= 22):
        return "Cáncer"
    elif (mes == 7 and dia >= 23) or (mes == 8 and dia <= 22):
        return "Leo"
    elif (mes == 8 and dia >= 23) or (mes == 9 and dia <= 22):
        return "Virgo"
    elif (mes == 9 and dia >= 23) or (mes == 10 and dia <= 22):
        return "Libra"
    elif (mes == 10 and dia >= 23) or (mes == 11 and dia <= 21):
        return "Escorpio"
    elif (mes == 11 and dia >= 22) or (mes == 12 and dia <= 21):
        return "Sagitario"
    elif (mes == 12 and dia >= 22) or (mes == 1 and dia <= 19):
        return "Capricornio"
    elif (mes == 1 and dia >= 20) or (mes == 2 and dia <= 18):
        return "Acuario"
    elif (mes == 2 and dia >= 19) or (mes == 3 and dia <= 20):
        return "Piscis"
    else:
        return "Error"


fecha_nacimiento_str = input("Introduce tu fecha de nacimiento en formato AAAA-MM-DD: ")
try:
    fecha_nacimiento = datetime.datetime.strptime(fecha_nacimiento_str, "%Y-%m-%d").date()
    signo = signo_solar(fecha_nacimiento)
    print(f"Tu signo solar es: {signo}")
except ValueError:
    print("Formato de fecha inválido.  Usa AAAA-MM-DD")

