import threading
import gensim
from gensim.models import LdaModel
import spacy
from .helper import log, topico_con_mas_score, textos_preparados_referencia, archivos_referencia_limpios, topicos_referencia
from gensim import corpora
textos_referencia = []
class ArchivoTxt:
    def __init__(self, nombre, extension, texto):
        self.nombre = nombre
        self.extension = extension
        self.texto = texto

def preparar_texto_para_lda(archivo, nlp, sw):
    archivo_mas_limpio = []
    for oracion in archivo:
        sustantivos = [token.lemma_ for token in nlp(oracion.lower()) if token.pos_ in ['NOUN'] and len(token.text) > 2]
        oracion_mas_limpia = [palabra for palabra in sustantivos if not palabra in sw and not str(palabra).isnumeric()]
        archivo_mas_limpio = archivo_mas_limpio + [palabra for palabra in oracion_mas_limpia if str(palabra) != '']
    return archivo_mas_limpio


# def obtener_sustantivos_lematizados(nlp, oracion):
#     texts_out = [token.lemma_ for token in nlp(oracion.lower()) if token.pos_ in ['NOUN'] and len(token.text) > 2]
#     return texts_out


def preparar_archivo_referencia_para_lda(archivo, nlp, sw):
    archivo_preparado = preparar_texto_para_lda(archivo.texto, nlp, sw)
    textos_referencia.append(ArchivoTxt(archivo.nombre, archivo.extension, archivo_preparado))
    textos_preparados_referencia.append(archivo_preparado)


def obtener_tema_del_texto(archivo_test, sw, cantidad_de_topicos):
    log.info("TOPICOS | Obteniendo topicos del texto ...")
    log.debug("TOPICOS | Preparando archivos para modelo LDA ...")
    nlp = spacy.load('es_core_news_sm')

    hilos_preparar_archivos_para_lda = list()
    for archivo in archivos_referencia_limpios:
        hilo_preparar_archivo_para_lda = threading.Thread(target=preparar_archivo_referencia_para_lda,
                                                          args=(archivo, nlp, sw,))
        hilos_preparar_archivos_para_lda.append(hilo_preparar_archivo_para_lda)
        hilo_preparar_archivo_para_lda.start()

    texto_preparado_test = preparar_texto_para_lda(archivo_test, nlp, sw)

    for index, thread in enumerate(hilos_preparar_archivos_para_lda):
        thread.join()

    log.debug("TOPICOS | Archivos de referencia preparados")
    log.debug("TOPICOS | Corriendo algoritmo LDA para archivos de referencia ...")
    diccionario = corpora.Dictionary(textos_preparados_referencia)
    corpus = [diccionario.doc2bow(texto) for texto in textos_preparados_referencia]
    modelo_lda = gensim.models.LdaMulticore(corpus, num_topics=10, id2word=diccionario, passes=2)

    log.debug("TOPICOS | Algoritmo LDA para archivos de referencia finalizado")
    
    log.debug("TOPICOS | Corriendo algoritmo LDA para archivos de test ...")
    indice, score = sorted(modelo_lda[diccionario.doc2bow(texto_preparado_test)], key=lambda tup: -1 * tup[1])[0]

    topico_con_mas_score.extend(
        [palabra.split("*")[1].replace("\"", "") for palabra in modelo_lda.print_topic(indice, cantidad_de_topicos).split(" + ")])

    log.info(f"TOPICOS | Topicos del texto: {topico_con_mas_score}")
    #log.warning("TOPICOS | Inicio de topicos para todos los textos.")
    #obtener_temas_de_textos_referencia(textos_preparados_referencia,archivos_referencia_limpios,cantidad_de_topicos,nlp,sw)

def obtener_temas_de_textos_referencia( textos_preparados_referencia,archivos_referencia_limpios, cantidad_de_topicos,nlp,sw):
    i = 0
    for archivo in textos_referencia:
        #texto_preparado = preparar_texto_para_lda(archivo.texto, nlp, sw)
        diccionario = corpora.Dictionary(textos_preparados_referencia)
        corpus = [diccionario.doc2bow(texto.texto) for texto in textos_referencia]
        modelo_lda = gensim.models.LdaMulticore(corpus, num_topics=cantidad_de_topicos, id2word=diccionario, passes=2)
        indice, score= sorted(modelo_lda[diccionario.doc2bow(archivo.texto)], key=lambda tup: -1 * tup[1])[0]
        topicos=[palabra.split("*")[1].replace("\"", "") for palabra in modelo_lda.print_topic(indice, cantidad_de_topicos).split(" + ")]
        i = i + 1 
        # print("el documento " + archivo.nombre + archivo.extension + f" contiene los siguientes topicos: {topicos}")
        topicos_referencia.append(topicos)

