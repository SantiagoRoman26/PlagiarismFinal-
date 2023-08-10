import threading
from .deteccion_de_plagio import obtener_oracion_mas_parecida_del_dataset, \
    obtener_oracion_mas_parecida_de_internet
from .helper import nombre_alumno, log, plagio_de_otros_tics, porcentajes_de_aparicion_otros_tics, \
    plagio_de_internet, porcentajes_de_aparicion_internet, preparar_oracion, archivos_referencia_limpios, titulo
from .extraer_datos import obtener_nombre_y_apellido_del_alumno, obtener_titulo_y_autor


def obtener_nombre_alumno(archivo, sw):
    log.info("NOMBRE_ALUMNO | Obteniendo nombre del alumno ...")
    nombre_alumno.extend(obtener_nombre_y_apellido_del_alumno(archivo, sw))
    if nombre_alumno:
        log.info("NOMBRE_ALUMNO | Alumno que realizo el ensayo: " + nombre_alumno[0])
    else:
        log.warning("NOMBRE_ALUMNO | No se encontro el nombre del alumno")

def obtener_titulo(archivo):
    log.info("TITULO | Obteniendo titulo del documento ...")
    titulo = obtener_titulo_y_autor(archivo)
    if titulo:
        log.warning("TITULO | Se encontro el titulo del ensayo: ")
    else:
        log.error("TITULO | No se encontro el titulo del ensayo")

def obtener_plagio_de_otros_tics(texto_archivo_test_limpio, sw):
    log.info("PLAGIO_DE_TICS | Obteniendo plagio de otros tics...")
    hilos_plagio_de_otros_tics = list()

    for oracion in texto_archivo_test_limpio:
        oracion_preparada = preparar_oracion(oracion, sw)
        if oracion_preparada is None:
            continue

        archivos_referencia = archivos_referencia_limpios
        hilo_plagio_de_otros_tics = threading.Thread(target=obtener_oracion_mas_parecida_del_dataset,
                                                    args=(oracion, oracion_preparada, texto_archivo_test_limpio, archivos_referencia, sw,))
        hilos_plagio_de_otros_tics.append(hilo_plagio_de_otros_tics)
        hilo_plagio_de_otros_tics.start()

    for index, thread in enumerate(hilos_plagio_de_otros_tics):
        thread.join()

    plagio_de_otros_tics.extend([(oracion, posible_plagio, porcentaje, archivo, ubicacion) for
                           (oracion, posible_plagio, porcentaje, archivo, ubicacion) in porcentajes_de_aparicion_otros_tics if
                           (porcentaje > 0.7)])
    log.info(f"PLAGIO_DE_TICS | {len(plagio_de_otros_tics)} plagios de otros tics encontrados")


def obtener_plagio_de_internet(texto_archivo_test_limpio, sw, cantidad_de_links, buscar_en_pdfs):
    log.info("PLAGIO_DE_INTERNET | Obteniendo plagio de paginas de internet...")
    hilos_plagio_de_internet = list()

    for oracion in texto_archivo_test_limpio:
        oracion_preparada = preparar_oracion(oracion, sw)
        if oracion_preparada is None:
            continue
        hilo_plagio_de_internet = threading.Thread(target=obtener_oracion_mas_parecida_de_internet,
                                                   args=(oracion, oracion_preparada, sw, cantidad_de_links, buscar_en_pdfs,))
        hilos_plagio_de_internet.append(hilo_plagio_de_internet)
        hilo_plagio_de_internet.start()

    for index, thread in enumerate(hilos_plagio_de_internet):
        thread.join()

    plagio_de_internet.extend([(oracion, posible_plagio, porcentaje, archivo, ubicacion) for
                          (oracion, posible_plagio, porcentaje, archivo, ubicacion) in porcentajes_de_aparicion_internet if
                          (porcentaje > 0.7)])
    log.info(f"PLAGIO_DE_INTERNET | {len(plagio_de_internet)} plagios de paginas de internet encontrados")
