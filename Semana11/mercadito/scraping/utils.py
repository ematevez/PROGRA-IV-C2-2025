import requests
from bs4 import BeautifulSoup
import random
from requests_html import HTMLSession
import asyncio
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import re

def comparar_precios(producto):
    # Simulación educativa de precios
    precio_coto = round(random.uniform(1000, 5000), 2)
    precio_dia = round(random.uniform(1000, 5000), 2)
    precio_carrefour = round(random.uniform(1000, 5000), 2)
    return {
        "producto": producto,
        "fuentes": [
            {"supermercado": "Coto", "precio": precio_coto, "url": "https://www.cotodigital.com.ar"},
            {"supermercado": "Día", "precio": precio_dia, "url": "https://diaonline.supermercadosdia.com.ar"},
            {"supermercado": "Carrefour", "precio": precio_carrefour, "url": "https://www.carrefour.com.ar"},
        ],
        "mejor_precio": min(precio_coto, precio_dia, precio_carrefour)
    }


"""
scraping/utils.py
Funciones de scraping para usar en Django
"""


def configurar_chrome():
    """Configuración de Chrome para scraping"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Sin ventana
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-logging")
    chrome_options.add_argument("--log-level=3")
    return chrome_options


def buscar_en_coto(producto):
    """
    Busca el primer producto en Coto Digital
    
    Args:
        producto (str): nombre del producto a buscar
    
    Returns:
        dict: información del producto o None si falla
    """
    driver = None
    try:
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=configurar_chrome()
        )
        
        url = f"https://www.cotodigital.com.ar/sitios/cdigi/browse?Ntt={producto}"
        driver.get(url)
        time.sleep(6)
        
        # Buscar primer producto con selectores de Coto
        primer_card = driver.find_element(By.CSS_SELECTOR, "catalogue-product")
        
        # Extraer nombre
        nombre = primer_card.find_element(By.CSS_SELECTOR, "h3.nombre-producto").text.strip()
        
        # Extraer precio
        precio_texto = primer_card.find_element(By.CSS_SELECTOR, "h4.card-title").text.strip()
        
        # Convertir precio a número
        precio_limpio = re.sub(r'[^\d,\.]', '', precio_texto)
        precio_limpio = precio_limpio.replace('.', '').replace(',', '.')
        precio_numerico = float(precio_limpio)
        
        # Extraer imagen
        imagen = primer_card.find_element(By.CSS_SELECTOR, "img.product-image").get_attribute('src')
        
        # Extraer link
        link_elem = primer_card.find_element(By.CSS_SELECTOR, "a")
        link = link_elem.get_attribute('href')
        
        driver.quit()
        
        return {
            "supermercado": "Coto Digital",
            "nombre": nombre,
            "precio": precio_texto,
            "precio_numerico": precio_numerico,
            "imagen": imagen,
            "link": link,
            "disponible": True
        }
        
    except Exception as e:
        print(f"Error en Coto: {str(e)}")
        if driver:
            driver.quit()
        return {
            "supermercado": "Coto Digital",
            "nombre": "No disponible",
            "precio": "N/A",
            "precio_numerico": 0,
            "imagen": None,
            "link": None,
            "disponible": False,
            "error": str(e)
        }


def buscar_en_carrefour(producto):
    """
    Busca el primer producto en Carrefour
    
    Args:
        producto (str): nombre del producto a buscar
    
    Returns:
        dict: información del producto o None si falla
    """
    driver = None
    try:
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=configurar_chrome()
        )
        
        url = f"https://www.carrefour.com.ar/{producto}"
        driver.get(url)
        time.sleep(7)
        
        # Buscar primer producto con selectores de Carrefour
        primer_card = driver.find_element(By.CSS_SELECTOR, "article.vtex-product-summary-2-x-element")
        
        # Extraer nombre
        try:
            nombre_elem = primer_card.find_element(By.CSS_SELECTOR, "h3.vtex-product-summary-2-x-productNameContainer span.vtex-product-summary-2-x-productBrand")
            nombre = nombre_elem.text.strip()
        except:
            nombre_elem = primer_card.find_element(By.CSS_SELECTOR, "h3")
            nombre = nombre_elem.text.strip()
        
        # Extraer precio
        precio_texto = "Precio no disponible"
        try:
            # Carrefour divide el precio en múltiples spans
            integers = primer_card.find_elements(By.CSS_SELECTOR, "span.valtech-carrefourar-product-price-0-x-currencyInteger")
            entero1 = integers[0].text if len(integers) > 0 else "0"
            entero2 = integers[1].text if len(integers) > 1 else "000"
            
            grupo = primer_card.find_element(By.CSS_SELECTOR, "span.valtech-carrefourar-product-price-0-x-currencyGroup").text
            decimal = primer_card.find_element(By.CSS_SELECTOR, "span.valtech-carrefourar-product-price-0-x-currencyDecimal").text
            fraccion = primer_card.find_element(By.CSS_SELECTOR, "span.valtech-carrefourar-product-price-0-x-currencyFraction").text
            
            precio_texto = f"${entero1}{grupo}{entero2}{decimal}{fraccion}"
        except:
            # Alternativa: buscar patrón en texto
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
        
        # Extraer imagen
        imagen = None
        try:
            img_elem = primer_card.find_element(By.CSS_SELECTOR, "img.vtex-product-summary-2-x-imageNormal")
            imagen = img_elem.get_attribute('src')
        except:
            try:
                img_elem = primer_card.find_element(By.CSS_SELECTOR, "img")
                imagen = img_elem.get_attribute('src')
            except:
                pass
        
        # Extraer link
        link = url
        try:
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
        
        return {
            "supermercado": "Carrefour",
            "nombre": nombre,
            "precio": precio_texto,
            "precio_numerico": precio_numerico,
            "imagen": imagen,
            "link": link,
            "disponible": True
        }
        
    except Exception as e:
        print(f"Error en Carrefour: {str(e)}")
        if driver:
            driver.quit()
        return {
            "supermercado": "Carrefour",
            "nombre": "No disponible",
            "precio": "N/A",
            "precio_numerico": 0,
            "imagen": None,
            "link": None,
            "disponible": False,
            "error": str(e)
        }


def comparar_precios1(producto):
    """
    Función principal que compara precios en Coto y Carrefour
    Compatible con Django views
    
    Args:
        producto (str): nombre del producto a buscar
    
    Returns:
        dict: comparación de precios entre ambos supermercados
    """
    print(f"Buscando: {producto}")
    
    # Buscar en ambos supermercados
    resultado_coto = buscar_en_coto(producto)
    resultado_carrefour = buscar_en_carrefour(producto)
    
    # Compilar resultados
    resultados = []
    if resultado_coto and resultado_coto.get('disponible'):
        resultados.append(resultado_coto)
    
    if resultado_carrefour and resultado_carrefour.get('disponible'):
        resultados.append(resultado_carrefour)
    
    # Determinar el más barato
    mas_barato = None
    diferencia = 0
    
    if len(resultados) >= 2:
        mas_barato = min(resultados, key=lambda x: x['precio_numerico'])
        precios = [r['precio_numerico'] for r in resultados if r['precio_numerico'] > 0]
        if len(precios) >= 2:
            diferencia = abs(max(precios) - min(precios))
    elif len(resultados) == 1:
        mas_barato = resultados[0]
    
    return {
        "producto_buscado": producto,
        "resultados": resultados,
        "mas_barato": mas_barato,
        "diferencia": diferencia,
        "total_encontrados": len(resultados)
    }
