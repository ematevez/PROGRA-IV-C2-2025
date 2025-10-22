"""
Comparador de Precios: Coto vs Carrefour
Busca el primer producto en ambos supermercados y compara
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import json
import re

def configurar_chrome():
    """Configuración común de Chrome"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-logging")
    chrome_options.add_argument("--log-level=3")
    return chrome_options


def buscar_en_coto(producto):
    """Busca en Coto Digital"""
    print(f"\n{'='*70}")
    print(f"🔍 BUSCANDO EN COTO: {producto}")
    print(f"{'='*70}\n")
    
    try:
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=configurar_chrome()
        )
        
        url = f"https://www.cotodigital.com.ar/sitios/cdigi/browse?Ntt={producto}"
        print("⏳ Cargando Coto Digital...")
        driver.get(url)
        time.sleep(6)
        
        print("🔎 Extrayendo datos...\n")
        
        # Buscar primer producto
        primer_card = driver.find_element(By.CSS_SELECTOR, "catalogue-product")
        
        # Nombre
        nombre = primer_card.find_element(By.CSS_SELECTOR, "h3.nombre-producto").text.strip()
        
        # Precio
        precio_texto = primer_card.find_element(By.CSS_SELECTOR, "h4.card-title").text.strip()
        
        # Precio numérico
        precio_limpio = re.sub(r'[^\d,\.]', '', precio_texto)
        precio_limpio = precio_limpio.replace('.', '').replace(',', '.')
        precio_numerico = float(precio_limpio)
        
        # Imagen
        imagen = primer_card.find_element(By.CSS_SELECTOR, "img.product-image").get_attribute('src')
        
        # Link
        link_elem = primer_card.find_element(By.CSS_SELECTOR, "a")
        link = "https://www.cotodigital.com.ar" + link_elem.get_attribute('href')
        
        driver.quit()
        
        resultado = {
            "supermercado": "Coto Digital",
            "nombre": nombre,
            "precio": precio_texto,
            "precio_numerico": precio_numerico,
            "imagen": imagen,
            "link": link
        }
        
        print("✅ ENCONTRADO EN COTO:")
        print(f"   📦 {nombre}")
        print(f"   💰 {precio_texto}")
        
        return resultado
        
    except Exception as e:
        print(f"❌ Error en Coto: {str(e)}")
        if 'driver' in locals():
            driver.quit()
        return None


def buscar_en_carrefour(producto):
    """Busca en Carrefour con los selectores correctos"""
    print(f"\n{'='*70}")
    print(f"🔍 BUSCANDO EN CARREFOUR: {producto}")
    print(f"{'='*70}\n")
    
    try:
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=configurar_chrome()
        )
        
        url = f"https://www.carrefour.com.ar/{producto}"
        print("⏳ Cargando Carrefour...")
        driver.get(url)
        time.sleep(7)  # Más tiempo para que cargue JavaScript
        
        print("🔎 Extrayendo datos...\n")
        
        # Buscar el primer article (basado en el HTML real)
        primer_card = driver.find_element(By.CSS_SELECTOR, "article.vtex-product-summary-2-x-element")
        
        # Extraer NOMBRE (h3 con clase productBrand)
        try:
            nombre_elem = primer_card.find_element(By.CSS_SELECTOR, "h3.vtex-product-summary-2-x-productNameContainer span.vtex-product-summary-2-x-productBrand")
            nombre = nombre_elem.text.strip()
        except:
            # Alternativa: buscar cualquier h3
            try:
                nombre_elem = primer_card.find_element(By.CSS_SELECTOR, "h3")
                nombre = nombre_elem.text.strip()
            except:
                nombre = "Nombre no disponible"
        
        # Extraer PRECIO (span con clase sellingPrice)
        precio_texto = "Precio no disponible"
        try:
            # Intentar extraer el precio completo
            precio_elem = primer_card.find_element(By.CSS_SELECTOR, "span.valtech-carrefourar-product-price-0-x-sellingPrice")
            
            # Carrefour divide el precio en múltiples spans
            # Extraer cada parte
            try:
                entero1 = primer_card.find_element(By.CSS_SELECTOR, "span.valtech-carrefourar-product-price-0-x-currencyInteger").text
                grupo = primer_card.find_element(By.CSS_SELECTOR, "span.valtech-carrefourar-product-price-0-x-currencyGroup").text
                
                # Buscar todos los integers (hay dos)
                integers = primer_card.find_elements(By.CSS_SELECTOR, "span.valtech-carrefourar-product-price-0-x-currencyInteger")
                entero2 = integers[1].text if len(integers) > 1 else "000"
                
                decimal = primer_card.find_element(By.CSS_SELECTOR, "span.valtech-carrefourar-product-price-0-x-currencyDecimal").text
                fraccion = primer_card.find_element(By.CSS_SELECTOR, "span.valtech-carrefourar-product-price-0-x-currencyFraction").text
                
                precio_texto = f"${entero1}{grupo}{entero2}{decimal}{fraccion}"
            except:
                # Si falla, usar el texto completo del elemento
                precio_texto = precio_elem.text.strip()
        except:
            # Última alternativa: buscar patrón $ en todo el texto
            texto = primer_card.text
            match = re.search(r'\$\s*[\d\.]+[\d,]+', texto)
            if match:
                precio_texto = match.group(0)
        
        # Convertir precio a número
        precio_numerico = 0
        try:
            precio_limpio = re.sub(r'[^\d,\.]', '', precio_texto)
            precio_limpio = precio_limpio.replace('.', '').replace(',', '.')
            precio_numerico = float(precio_limpio)
        except:
            pass
        
        # Extraer IMAGEN
        imagen = None
        try:
            img_elem = primer_card.find_element(By.CSS_SELECTOR, "img.vtex-product-summary-2-x-imageNormal")
            imagen = img_elem.get_attribute('src')
        except:
            try:
                # Alternativa: buscar cualquier img
                img_elem = primer_card.find_element(By.CSS_SELECTOR, "img")
                imagen = img_elem.get_attribute('src')
            except:
                pass
        
        # Extraer LINK
        link = url
        try:
            # Buscar el link de la imagen
            link_elem = primer_card.find_element(By.CSS_SELECTOR, "a")
            href = link_elem.get_attribute('href')
            if href:
                if not href.startswith('http'):
                    link = f"https://www.carrefour.com.ar{href}"
                else:
                    link = href
        except:
            pass
        
        driver.quit()
        
        resultado = {
            "supermercado": "Carrefour",
            "nombre": nombre,
            "precio": precio_texto,
            "precio_numerico": precio_numerico,
            "imagen": imagen,
            "link": link
        }
        
        print("✅ ENCONTRADO EN CARREFOUR:")
        print(f"   📦 {nombre}")
        print(f"   💰 {precio_texto}")
        
        return resultado
        
    except Exception as e:
        print(f"❌ Error en Carrefour: {str(e)}")
        if 'driver' in locals():
            driver.quit()
        return None


def comparar_precios(producto):
    """
    Busca en ambos supermercados y compara precios
    """
    print(f"\n{'='*70}")
    print(f"🛒 COMPARANDO PRECIOS: {producto.upper()}")
    print(f"{'='*70}")
    
    # Buscar en Coto
    resultado_coto = buscar_en_coto(producto)
    
    # Buscar en Carrefour
    resultado_carrefour = buscar_en_carrefour(producto)
    
    # Compilar resultados
    comparacion = {
        "producto_buscado": producto,
        "fecha_busqueda": time.strftime("%Y-%m-%d %H:%M:%S"),
        "resultados": []
    }
    
    if resultado_coto:
        comparacion["resultados"].append(resultado_coto)
    
    if resultado_carrefour:
        comparacion["resultados"].append(resultado_carrefour)
    
    # Determinar el más barato
    if len(comparacion["resultados"]) >= 2:
        mas_barato = min(comparacion["resultados"], key=lambda x: x['precio_numerico'])
        comparacion["mas_barato"] = mas_barato["supermercado"]
        comparacion["diferencia"] = abs(
            comparacion["resultados"][0]["precio_numerico"] - 
            comparacion["resultados"][1]["precio_numerico"]
        )
    elif len(comparacion["resultados"]) == 1:
        comparacion["mas_barato"] = comparacion["resultados"][0]["supermercado"]
        comparacion["diferencia"] = 0
    else:
        comparacion["mas_barato"] = None
        comparacion["diferencia"] = 0
    
    return comparacion


def mostrar_comparacion(comparacion):
    """Muestra la comparación en pantalla"""
    print(f"\n{'='*70}")
    print("📊 COMPARACIÓN DE PRECIOS")
    print(f"{'='*70}\n")
    
    if not comparacion["resultados"]:
        print("❌ No se encontraron resultados")
        return
    
    for i, resultado in enumerate(comparacion["resultados"], 1):
        print(f"{i}. {resultado['supermercado'].upper()}")
        print(f"   📦 Producto: {resultado['nombre']}")
        print(f"   💰 Precio: {resultado['precio']} (${resultado['precio_numerico']:.2f})")
        print(f"   🖼️  Imagen: {'✓' if resultado['imagen'] else '✗'}")
        print(f"   🔗 Link: {resultado['link'][:60]}...")
        print()
    
    if comparacion["mas_barato"]:
        print(f"{'='*70}")
        print(f"🏆 MÁS BARATO: {comparacion['mas_barato'].upper()}")
        if comparacion["diferencia"] > 0:
            print(f"💵 Te ahorrás: ${comparacion['diferencia']:.2f}")
        print(f"{'='*70}\n")


def guardar_comparacion(comparacion, producto):
    """Guarda la comparación en JSON y TXT"""
    
    # Guardar JSON
    archivo_json = f"comparacion_{producto}.json"
    with open(archivo_json, 'w', encoding='utf-8') as f:
        json.dump(comparacion, f, indent=2, ensure_ascii=False)
    print(f"✓ JSON guardado: {archivo_json}")
    
    # Guardar TXT
    archivo_txt = f"comparacion_{producto}.txt"
    with open(archivo_txt, 'w', encoding='utf-8') as f:
        f.write("="*70 + "\n")
        f.write(f"COMPARACIÓN DE PRECIOS: {producto.upper()}\n")
        f.write(f"Fecha: {comparacion['fecha_busqueda']}\n")
        f.write("="*70 + "\n\n")
        
        for i, resultado in enumerate(comparacion["resultados"], 1):
            f.write(f"{i}. {resultado['supermercado']}\n")
            f.write(f"   Producto: {resultado['nombre']}\n")
            f.write(f"   Precio:   {resultado['precio']}\n")
            f.write(f"   Link:     {resultado['link']}\n")
            if resultado['imagen']:
                f.write(f"   Imagen:   {resultado['imagen']}\n")
            f.write("\n")
        
        if comparacion["mas_barato"]:
            f.write("="*70 + "\n")
            f.write(f"MÁS BARATO: {comparacion['mas_barato']}\n")
            if comparacion["diferencia"] > 0:
                f.write(f"Ahorro: ${comparacion['diferencia']:.2f}\n")
            f.write("="*70 + "\n")
    
    print(f"✓ TXT guardado: {archivo_txt}\n")


if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║          COMPARADOR DE PRECIOS: COTO VS CARREFOUR             ║
    ║           Busca en ambos y te dice dónde conviene             ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Pedir producto
    producto = input("\n¿Qué producto querés comparar? (ej: leche, arroz, pan): ").strip()
    
    if not producto:
        print("❌ Debes ingresar un producto")
    else:
        # Comparar precios
        comparacion = comparar_precios(producto)
        
        # Mostrar resultados
        mostrar_comparacion(comparacion)
        
        # Guardar
        guardar = input("¿Guardar comparación? (s/n) [s]: ").strip().lower() or 's'
        if guardar == 's':
            guardar_comparacion(comparacion, producto)
        
        print(f"\n{'='*70}")
        print("✅ PROCESO COMPLETADO")
        print(f"{'='*70}\n")