import math
import re
from collections import Counter
from sklearn.neural_network import MLPRegressor
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity



def obtener_similitud_del_coseno(vector1, vector2):
    interseccion = set(vector1.keys()) & set(vector2.keys())
    numerador = sum([vector1[x] * vector2[x] for x in interseccion])

    sum1 = sum([vector1[x] ** 2 for x in vector1.keys()])
    sum2 = sum([vector2[x] ** 2 for x in vector2.keys()])
    denominador = math.sqrt(sum1) * math.sqrt(sum2)

    if not denominador:
        return 0.0
    else:
        return float(numerador) / denominador


def string_a_vector(texto):
    palabras = re.compile(r'\w+').findall(texto)
    return Counter(palabras)


def obtener_similitud(texto1, texto2):
    vector1 = string_a_vector(texto1)
    vector2 = string_a_vector(texto2)
    return obtener_similitud_del_coseno(vector1, vector2)

def similitud(archivo_test_txt, archivos_referencia ): #similitud_red_neuronal
    #vectorize = lambda Text: TfidfVectorizer().fit_transform(Text).toarray()
    vectorizer = TfidfVectorizer().fit_transform([archivo_test_txt, archivos_referencia])
    y = [0,0]
    nn_model = MLPRegressor(hidden_layer_sizes=(50,), max_iter=500, alpha=0.01,
                        solver='adam', verbose=False, tol=0.0001, random_state=42)
    #similarity = lambda doc1, doc2: cosine_similarity([doc1, doc2])
    nn_model.fit(vectorizer.toarray(),[y,y])
    sim_score = cosine_similarity(vectorizer)
    return float(sim_score[0][1])
