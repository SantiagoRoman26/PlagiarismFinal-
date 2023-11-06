import nltk
import spacy
import itertools
import re
from nltk import word_tokenize


def obtener_nombre_y_apellido_del_alumno(texto_dividido_en_oraciones, sw):
    nlp = spacy.load('es_core_news_sm')

    lineas_pasadas_por_el_modelo = [[(a.text, a.label_) for a in nlp(oracion).ents] for oracion in texto_dividido_en_oraciones]
    lista_flatenizada = list(itertools.chain.from_iterable(lineas_pasadas_por_el_modelo))

    entidades_reconocidas_como_personas = [texto for (texto, categoria) in lista_flatenizada if categoria == 'PER']

    entidades_reconocidas_como_personas = [entidad for entidad in entidades_reconocidas_como_personas if not entidad.lower().strip() in sw]

    posibles_nombres_alumno = []

    for entidad in entidades_reconocidas_como_personas:
        contextos = nltk.Text(word_tokenize(". ".join(texto_dividido_en_oraciones))).concordance_list(entidad.split(' ', 1)[0])
        for contexto in contextos:
            if list(map(str.lower, contexto.left)).__contains__('alumno') or \
               list(map(str.lower, contexto.left)).__contains__('alumna') or \
               list(map(str.lower, contexto.left)).__contains__('integrante') or \
               list(map(str.lower, contexto.left)).__contains__('apellido') or \
               list(map(str.lower, contexto.left)).__contains__('nombre'):
                posibles_nombres_alumno += [entidad]
    if posibles_nombres_alumno:
        return posibles_nombres_alumno
    else:
        return entidades_reconocidas_como_personas



def obtener_titulo_y_autor(oraciones_limpias):
    # Unir las oraciones en un solo texto
    contenido_limpio = ' '.join(oraciones_limpias)

    # Patrón para encontrar el título del trabajo
    patron_titulo = r'\b(?:Universidad|Facultad|Carrera)\b: (.+?)\.'

    # Patrón para encontrar el autor del trabajo
    patron_autor = r'Autor:\s+(.+)'

    # Buscar el título y el autor utilizando expresiones regulares
    match_titulo = re.search(patron_titulo, contenido_limpio)
    match_autor = re.search(patron_autor, contenido_limpio)

    titulo = match_titulo.group(1).strip() if match_titulo else None
    autor = match_autor.group(1).strip() if match_autor else None

    # print("TITULO",titulo)
    # print("AUTOR",autor)
    return titulo, autor