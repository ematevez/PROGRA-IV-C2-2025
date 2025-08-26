import math

def calcular_perimetro_cuadrado(lado):
  """Calcula el perímetro de un cuadrado."""
  return 4 * lado

def calcular_area_cuadrado(lado):
  """Calcula el área de un cuadrado."""
  return lado * lado

def calcular_perimetro_rectangulo(base, altura):
  """Calcula el perímetro de un rectángulo."""
  return 2 * (base + altura)

def calcular_area_rectangulo(base, altura):
  """Calcula el área de un rectángulo."""
  return base * altura

def calcular_perimetro_circulo(radio):
  """Calcula el perímetro (circunferencia) de un círculo."""
  return 2 * math.pi * radio

def calcular_area_circulo(radio):
  """Calcula el área de un círculo."""
  return math.pi * radio**2

def calcular_perimetro_triangulo(lado1, lado2, lado3):
  """Calcula el perímetro de un triángulo."""
  return lado1 + lado2 + lado3

def calcular_area_triangulo(base, altura):
  """Calcula el área de un triángulo."""
  return (base * altura) / 2


def mostrar_menu():
  """Muestra el menú de opciones al usuario."""
  print("\n--- Menú de Cálculos Geométricos ---")
  print("1. Cuadrado")
  print("2. Rectángulo")
  print("3. Círculo")
  print("4. Triángulo")
  print("5. Salir")
  print("----------------------------------")


def obtener_datos_cuadrado():
  """Obtiene los datos necesarios para calcular el área y perímetro de un cuadrado."""
  while True:
    try:
      lado = float(input("Ingrese la longitud del lado del cuadrado: "))
      if lado > 0:
        return lado
      else:
        print("El lado debe ser un número positivo.")
    except ValueError:
      print("Entrada inválida. Ingrese un número.")


def obtener_datos_rectangulo():
  """Obtiene los datos necesarios para calcular el área y perímetro de un rectángulo."""
  while True:
    try:
      base = float(input("Ingrese la base del rectángulo: "))
      altura = float(input("Ingrese la altura del rectángulo: "))
      if base > 0 and altura > 0:
        return base, altura
      else:
        print("La base y la altura deben ser números positivos.")
    except ValueError:
      print("Entrada inválida. Ingrese números.")


def obtener_datos_circulo():
  """Obtiene los datos necesarios para calcular el área y perímetro de un círculo."""
  while True:
    try:
      radio = float(input("Ingrese el radio del círculo: "))
      if radio > 0:
        return radio
      else:
        print("El radio debe ser un número positivo.")
    except ValueError:
      print("Entrada inválida. Ingrese un número.")


def obtener_datos_triangulo():
    """Obtiene los datos necesarios para calcular el área y perímetro de un triángulo."""
    while True:
        try:
            lado1 = float(input("Ingrese la longitud del lado 1 del triángulo: "))
            lado2 = float(input("Ingrese la longitud del lado 2 del triángulo: "))
            lado3 = float(input("Ingrese la longitud del lado 3 del triángulo: "))
            base = float(input("Ingrese la base del triángulo: "))
            altura = float(input("Ingrese la altura del triángulo: "))
            if lado1 > 0 and lado2 > 0 and lado3 > 0 and base > 0 and altura > 0:
                return lado1, lado2, lado3, base, altura
            else:
                print("Las longitudes de los lados y la base y altura deben ser números positivos.")
        except ValueError:
            print("Entrada inválida. Ingrese números.")


while True:
  mostrar_menu()
  opcion = input("Seleccione una opción: ")

  if opcion == '1':
    lado = obtener_datos_cuadrado()
    perimetro = calcular_perimetro_cuadrado(lado)
    area = calcular_area_cuadrado(lado)
    print(f"Perímetro del cuadrado: {perimetro}")
    print(f"Área del cuadrado: {area}")

  elif opcion == '2':
    base, altura = obtener_datos_rectangulo()
    perimetro = calcular_perimetro_rectangulo(base, altura)
    area = calcular_area_rectangulo(base, altura)
    print(f"Perímetro del rectángulo: {perimetro}")
    print(f"Área del rectángulo: {area}")

  elif opcion == '3':
    radio = obtener_datos_circulo()
    perimetro = calcular_perimetro_circulo(radio)
    area = calcular_area_circulo(radio)
    print(f"Perímetro (circunferencia) del círculo: {perimetro}")
    print(f"Área del círculo: {area}")

  elif opcion == '4':
    lado1, lado2, lado3, base, altura = obtener_datos_triangulo()
    perimetro = calcular_perimetro_triangulo(lado1, lado2, lado3)
    area = calcular_area_triangulo(base, altura)
    print(f"Perímetro del triángulo: {perimetro}")
    print(f"Área del triángulo: {area}")

  elif opcion == '5':
    print("Saliendo del programa...")
    break

  else:
    print("Opción inválida. Intente de nuevo.")
