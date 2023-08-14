import datetime
import os
import sys
import threading
import time
import yaml
from nltk.corpus import stopwords
from .funciones_principales import obtener_nombre_alumno, obtener_plagio_de_otros_tics, obtener_plagio_de_internet, obtener_titulo
from .helper import *
from .procesamiento_de_archivos import obtener_archivos, guardar_resultado, limpieza, \
    limpiar_archivos_referencia, excluida, correctamente_citada,obtener_archivo_Test
from .tema_del_texto import obtener_tema_del_texto
from .redes_neuronales import generar_modelo_entrenado


# def main():
def main(directorio_archivo):
    log.info("Iniciando detector de plagio ...")
    tiempo_inicial = time.time()
    # Obtener la ruta absoluta del archivo config.yml
    config_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "config.yml"))
    # generar la ruta base
    base_dir = os.path.dirname(config_file_path)
    print('base dir =',base_dir)
    with open(config_file_path, "r") as ymlfile:
        config = yaml.load(ymlfile, Loader=yaml.FullLoader)
    log.warning("INFO | Obteniendo documentos de la carpeta.")
    print(os.path.join(base_dir,config["path_archivos_referencia"]))
    archivos_referencia = obtener_archivos(os.path.join(base_dir,config["path_archivos_referencia"]))
    if not archivos_referencia:
        log.warning("No se encontraron archivos en la carpeta referencia, solo se buscara plagio de Internet")
    log.warning("INFO | Fin de generar los documentos de la carpeta.")
    # archivos_test = obtener_archivos(os.path.join(base_dir,config["path_archivo_test"]))
    archivos_test = obtener_archivo_Test(directorio_archivo)
    if archivos_test:
        archivo_test = archivos_test[0]
        nombre_archivo = archivo_test.nombre + archivo_test.extension
        log.info("Analizando plagio en: " + nombre_archivo)
        texto_archivo_test_limpio = limpieza(archivo_test.texto)
        obtener_titulo(archivo_test.texto)
        print(texto_archivo_test_limpio)
        #print(f"oraciones limpias: {texto_archivo_test_limpio}")
        texto_archivo_test_sin_oraciones_excluidas = [oracion for oracion in texto_archivo_test_limpio if not excluida(oracion,base_dir+'/')]

        sw = stopwords.words('spanish')

        hilos_limpieza_archivos_referencia = list()

        for archivo in archivos_referencia:
            if archivo is not None:
                hilo_limpieza_archivos = threading.Thread(target=limpiar_archivos_referencia, args=(archivo,))
                hilos_limpieza_archivos_referencia.append(hilo_limpieza_archivos)
                hilo_limpieza_archivos.start()

        hilos_principales = list()

        hilo_nombre_alumno = threading.Thread(target=obtener_nombre_alumno, args=(texto_archivo_test_limpio, sw,))
        hilos_principales.append(hilo_nombre_alumno)
        hilo_nombre_alumno.start()
        
        hilos_red_nuronal = list() #nuevo 
        
        

        # hilo_plagio_de_internet = threading.Thread(target=obtener_plagio_de_internet,
        #                                           args=(texto_archivo_test_sin_oraciones_excluidas, sw, int(config["cantidad_de_links"]), bool(config["buscar_en_pdfs"]),))
        # hilos_principales.append(hilo_plagio_de_internet)
        # hilo_plagio_de_internet.start()

        for index, thread in enumerate(hilos_limpieza_archivos_referencia):
            thread.join()

        # hilos_limpieza_archivos_entrenamiento = list()

        # for archivo in archivos_referencia:
        #     if archivo is not None:
        #         hilo_limpieza_archivos = threading.Thread(target=algo, args=(archivo,))
        #         hilos_limpieza_archivos_entrenamiento.append(hilo_limpieza_archivos)
        #         hilo_limpieza_archivos.start()

        # for index, thread in enumerate(hilos_limpieza_archivos_entrenamiento):
        #     thread.join()

        # log.warning("INFO | Entrenamiento del modelo ....")                                                                                     #nuevo
        # hilo_red_nuronal = threading.Thread(target=generar_modelo_entrenado, args=(os.path.join(base_dir,config["pares_textos_path"], ))                              #nuevo
        # hilos_red_nuronal.append(hilo_red_nuronal)                                                                                              #nuevo
        # hilo_red_nuronal.start()                                                                                                                #nuevo
        

        # for index, thread in enumerate(hilos_red_nuronal):
        #     thread.join()
        # log.info("INFO | FIn del entrenamiento del modelo")
        
        # hilo_tema = threading.Thread(target=obtener_tema_del_texto,
        #                             args=(texto_archivo_test_limpio, sw, int(config["cantidad_de_topicos"]),))
        # hilos_principales.append(hilo_tema)
        # hilo_tema.start()

        hilo_plagio_de_otros_tics = threading.Thread(target=obtener_plagio_de_otros_tics,
                                                    args=(texto_archivo_test_sin_oraciones_excluidas, sw, ))
        hilos_principales.append(hilo_plagio_de_otros_tics)
        hilo_plagio_de_otros_tics.start()

        for index, thread in enumerate(hilos_principales):
            thread.join()

        print("Obteniendo resultados finales ...")

        plagio = plagio_de_otros_tics.copy()
        for (oracion, posible_plagio, porcentaje, url, ubicacion) in plagio_de_internet:
            if not any(oracion == otra_oracion for (otra_oracion, _, _, _, _) in plagio):
                if not correctamente_citada(url, texto_archivo_test_limpio):
                    plagio += [(oracion, posible_plagio, porcentaje, url, ubicacion)]

        obtener_titulo(texto_archivo_test_limpio)

        tiempo_final = time.time()
        tiempo_que_tardo_str = str(datetime.timedelta(seconds=tiempo_final-tiempo_inicial)).split(":")
        if tiempo_que_tardo_str[1] == "00":
            tiempo_que_tardo = f"{tiempo_que_tardo_str[2].split('.')[0]} segundos"
        else:
            tiempo_que_tardo = f"{tiempo_que_tardo_str[1]} minutos, {tiempo_que_tardo_str[2].split('.')[0]} segundos"
        log.info(f"Total de {len(plagio)} plagios encontrados en {tiempo_que_tardo}")

        # porcentaje_de_plagio = int((len(plagio) * 100) / len(texto_archivo_test_limpio))
        porcentaje_de_plagio = 0
        for oracion, plagios, porcentaje, url, ubicacion in plagio:
            porcentaje_de_plagio += porcentaje
        try:
            porcentaje_de_plagio = (porcentaje_de_plagio / len(plagio)) *100
        except ZeroDivisionError:
            porcentaje_de_plagio = 0

        log.warning(f"num oraciones: {len(texto_archivo_test_limpio)}")
        documento_generado,nombre =guardar_resultado(nombre_archivo, topico_con_mas_score, plagio, tiempo_que_tardo, porcentaje_de_plagio, os.path.join(base_dir,config["path_resultado"]), os.path.join(base_dir,config["path_archivos_referencia"])) #aqui
        informacion ={
            "nombre_archivo":nombre_archivo, 
            "topico_con_mas_score":topico_con_mas_score, 
            "tiempo_que_tardo":tiempo_que_tardo, 
            "porcentaje_de_plagio":porcentaje_de_plagio, 
            "path_resultado":os.path.join(base_dir,config["path_resultado"]), 
            "path_referencia":os.path.join(base_dir,config["path_archivos_referencia"]), 
            "total_oraciones":len(texto_archivo_test_limpio)
            }
        
        log.info("El detector de plagio finalizo correctamente!")
        log.warning(documento_generado)
        log.info(f"Porcentaje de plagio: {porcentaje_de_plagio} %")
        log.info(f'Resultado guardado en: {os.path.abspath(os.path.join(base_dir,config["path_resultado"]))}\\Plagio {str(str(nombre_archivo).split(".")[0])}.docx')
        print ('nombre alumno ', nombre_alumno)
        return documento_generado, nombre, plagio, informacion
    else:
        log.error("No se encontro ningun archivo para verificar plagio")
        log.error("Cerrando detector de plagio...")

def regenerarResultado(nombre_archivo,  topico_con_mas_score, plagio, tiempo_que_tardo, porcentaje_de_plagio, path_resultado, path_referencia, nombre_documento_anterior):
    os.remove(nombre_documento_anterior)
    documento_generado,nombre = guardar_resultado(nombre_archivo,  topico_con_mas_score, plagio, tiempo_que_tardo, porcentaje_de_plagio, path_resultado, path_referencia)
    return documento_generado, nombre


if __name__ == '__main__':
    main()
