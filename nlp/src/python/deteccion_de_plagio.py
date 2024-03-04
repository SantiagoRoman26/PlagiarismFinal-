import time
import requests
import googlesearch
from bs4 import BeautifulSoup
from nltk import word_tokenize
from .metodos_de_similitud import obtener_similitud, similitud
from .helper import porcentajes_de_aparicion_internet, log, porcentajes_de_aparicion_otros_tics, preparar_oracion, mutex
from .procesamiento_de_archivos import limpieza
from .redes_neuronales import calcular_similitud
import concurrent.futures


def obtener_oracion_mas_parecida_del_dataset(oracion, oracion_preparada, archivo_test_txt, archivos_referencia, sw):
    mayor_porcentaje = 0.0
    oracion_mas_parecida = ''
    archivo_donde_se_encontro = ''
    archivo_donde_se_encontro_txt = ''
    ubicacion_dentro_de_la_lista = 0

    for archivo in archivos_referencia:
        if archivo is not None:

            # numero = calcular_similitud(".".join(archivo_test_txt), ".".join(archivo.texto))
            numero = obtener_similitud(".".join(archivo_test_txt), ".".join(archivo.texto))
            if  numero > 0.8: #mayor
                # print("numero= "+ str(numero))

                for oracion_a_comparar in archivo.texto:
                    oracion_a_comparar_preparada = preparar_oracion(oracion_a_comparar, sw)
                    if oracion_a_comparar_preparada is None:
                        continue
                    similitud_textos = obtener_similitud(oracion_preparada, oracion_a_comparar_preparada)
                    
                    if similitud_textos > mayor_porcentaje:
                        mayor_porcentaje = similitud_textos
                        oracion_mas_parecida = oracion_a_comparar
                        archivo_donde_se_encontro = archivo.nombre + archivo.extension
                        ubicacion_dentro_de_la_lista = int(archivo.texto.index(oracion_a_comparar))
                        #ubicacion_dentro_de_la_lista = int(archivo_test_txt.index(oracion_preparada))
                        archivo_donde_se_encontro_txt = archivo.texto
    ubicacion_principio = sum(map(len, map(word_tokenize, archivo_donde_se_encontro_txt[:ubicacion_dentro_de_la_lista])))
    ubicacion_fin = ubicacion_principio + len(word_tokenize(oracion_mas_parecida))
    ubicacion_donde_se_encontro = f"({ubicacion_principio}, {ubicacion_fin})"
    porcentajes_de_aparicion_otros_tics.append((oracion, oracion_mas_parecida, mayor_porcentaje, archivo_donde_se_encontro, ubicacion_donde_se_encontro))


def obtener_html_como_texto(url):
    try:
        response = requests.get(url)
        html = requests.get(url).text
    except requests.exceptions.ConnectionError:
        print("error obteniendo url")
        return ''
    if response.status_code == 200:
        soup = BeautifulSoup(html, features='lxml')
        for script in soup(["script", "style"]):
            script.extract()
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        return text
    else:
        return ''

def obtener_oracion_mas_parecida_de_internet(oracion, oracion_preparada, sw, cantidad_de_links, buscar_en_pdfs):
    mayor_porcentaje = 0.0
    oracion_mas_parecida = ''
    url_donde_se_encontro = ''
    archivo_donde_se_encontro = ''
    ubicacion_dentro_de_la_lista = 0

    #mutex.acquire()
    def buscar_en_internet(url):
        nonlocal mayor_porcentaje, oracion_mas_parecida, url_donde_se_encontro, archivo_donde_se_encontro, ubicacion_dentro_de_la_lista  
        try:
            #for url in googlesearch.search(oracion_preparada, num_results=cantidad_de_links, lang= "es", sleep_interval=15):
            for url in googlesearch.search(oracion_preparada, lang= "es", tld='com', num=cantidad_de_links, stop=cantidad_de_links, pause=15.0, verify_ssl = False):
                print("url:",url)
                time.sleep(0.2)
                #mutex.release()
                if (not buscar_en_pdfs) and url.endswith(".pdf") or str(url).endswith(".pdf/"):
                    #mutex.acquire()
                    continue
                else:
                    texto = obtener_html_como_texto(url)
                    if texto != '':
                        archivo = limpieza(texto)
                        if len(archivo) > 20000:
                            log.info(f"PLAGIO_DE_INTERNET |Archivo web demasiado extenso omitiendo")
                            continue
                        for oracion_a_comparar in archivo:
                            oracion_a_comparar_preparada = preparar_oracion(oracion_a_comparar, sw)
                            if oracion_a_comparar_preparada is None:
                                continue
                            similitud = obtener_similitud(oracion_preparada, oracion_a_comparar_preparada)
                            if similitud > 0.8:
                                mayor_porcentaje = similitud
                                oracion_mas_parecida = oracion_a_comparar
                                url_donde_se_encontro = url
                                archivo_donde_se_encontro = archivo
                                ubicacion_dentro_de_la_lista = int(archivo.index(oracion_a_comparar))
                                break
                            elif similitud > mayor_porcentaje:
                                mayor_porcentaje = similitud
                                oracion_mas_parecida = oracion_a_comparar
                                url_donde_se_encontro = url
                                archivo_donde_se_encontro = archivo
                                ubicacion_dentro_de_la_lista = int(archivo.index(oracion_a_comparar))
                        print("fin for")
                if mayor_porcentaje > 0.8:
                    #mutex.acquire()
                    print("break")
                    break

                #mutex.acquire()
        except Exception as e:
            print("error:",e)
            time.sleep(3)  
    # Límite de tiempo de 600 segundos (10 minutos)
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(buscar_en_internet, None)
        try:
            result = future.result(timeout=200)
        except concurrent.futures.TimeoutError:
            print("Se alcanzó el límite de tiempo. La búsqueda en Internet se detendrá.")
            

    time.sleep(0.2)
    try:
        None
        #mutex.release()
    except Exception as e:
        None
    ubicacion_principio = sum(map(len, map(word_tokenize, archivo_donde_se_encontro[:ubicacion_dentro_de_la_lista])))
    ubicacion_fin = ubicacion_principio + len(word_tokenize(oracion_mas_parecida))
    ubicacion_donde_se_encontro = f"({ubicacion_principio}, {ubicacion_fin})"
    porcentajes_de_aparicion_internet.append((oracion, oracion_mas_parecida, mayor_porcentaje, url_donde_se_encontro, ubicacion_donde_se_encontro))
