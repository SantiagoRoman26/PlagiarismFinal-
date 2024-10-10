import os               #mmmm
import numpy as np
from .helper import archivos_referencia_limpios, modelo_entrenado #cambiar 


from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from keras.preprocessing.text import Tokenizer
from keras_preprocessing.sequence import pad_sequences                      #Importante
from keras.models import Model
from keras.layers import Dense, Embedding, Flatten, Concatenate, Input, Dropout
from keras.optimizers import Adam

def generar_pares_textos(pares_textos_path, documentos):                #fuera
    #cuidado, posible implementacion de deteccion_de_plagio  para proseguir
    sample_files = [doc.nombre + doc.extension for doc in documentos]
    sample_contents = [".".join(doc.texto) for doc in documentos]
    sample_contents_lemmatized = sample_contents

    vectorize = lambda Text: TfidfVectorizer(max_features=10000, ngram_range=(1, 2), sublinear_tf=True, smooth_idf=True).fit_transform(Text).toarray()
    similarity = lambda doc1, doc2: cosine_similarity([doc1, doc2])

    vectors = vectorize(sample_contents_lemmatized)
    s_vectors = list(zip(sample_files, vectors))

    results = set()
    for sample_a, text_vector_a in s_vectors:
        new_vectors = s_vectors.copy()
        current_index = new_vectors.index((sample_a, text_vector_a))
        del new_vectors[current_index]
        for sample_b, text_vector_b in new_vectors:
            sim_score = similarity(text_vector_a, text_vector_b)[0][1]
            sample_pair = sorted((sample_a, sample_b))
            score = sample_pair[0], sample_pair[1], sim_score
            results.add(score)

    with open(os.path.join(pares_textos_path, "pares_textos.txt"), 'w') as f:
        for data in results:
            print(data, file=f)

def leer_pares_textos(pares_textos_path, documentos):
    text_pairs = []
    train_text1 = []
    train_text2 = []
    train_similarity = []
    with open(pares_textos_path + "pares_textos.txt", "r") as file: #ojo
        for line in file:
            line = line.strip().strip('()').replace("'", "")
            texto1, texto2, sim = line.split(", ")
            doc1 = texto1
            doc2 = texto2
            similarity = float(sim)
            text_pairs.append((doc1, doc2, similarity))

    for pair in text_pairs:
        doc1 = pair[0]
        doc2 = pair[1]
        similarity = pair[2]

        # Leer el texto en los documentos
        documento1 = documento_por_nombre(documentos, doc1)
        documento2 = documento_por_nombre(documentos, doc2)

        if documento1 and documento2:
            # Ambos documentos encontrados, se pueden acceder a sus atributos
            text1 = documento1.texto
            text2 = documento2.texto

            train_text1.append(text1)
            train_text2.append(text2)
            train_similarity.append(similarity)
        else:
            # Alguno de los documentos no se encontró, manejar el caso en consecuencia
            print(f"Error: No se encontró el documento para la pareja {doc1} y {doc2}")

        

    train_similarity = np.array(train_similarity)

    return train_text1, train_text2, train_similarity

def documento_por_nombre(documentos, nombre_documento):
    for doc in documentos:
        if doc.nombre + doc.extension == nombre_documento:
            return doc
    return None

def generar_modelo_entrenado(pares_textos_path):
    
    # Ingresar el numero maximo de palabras a considerar
    max_words = 10000
    train_text1 = []
    train_text2 = []
    train_similarity = []
    documentos = archivos_referencia_limpios
    generar_pares_textos(pares_textos_path, documentos)
    train_text1, train_text2, train_similarity = leer_pares_textos(pares_textos_path, documentos)

    tokenizer = Tokenizer(num_words=max_words)
    tokenizer.fit_on_texts(train_text1 + train_text2)
    
    train_sequences1 = tokenizer.texts_to_sequences(train_text1)
    train_sequences2 = tokenizer.texts_to_sequences(train_text2)
    
    train_data1 = pad_sequences(train_sequences1)
    train_data2 = pad_sequences(train_sequences2)
    
    embedding_dim = 100 #200
    hidden_units = 128 #256
    dropout_rate = 0.2
    
    input1 = Input(shape=(train_data1.shape[1],))
    input2 = Input(shape=(train_data2.shape[1],))
    
    shared_embedding_layer = Embedding(max_words, embedding_dim)
    
    embedded1 = shared_embedding_layer(input1)
    embedded2 = shared_embedding_layer(input2)
    
    flattened1 = Flatten()(embedded1)
    flattened2 = Flatten()(embedded2)
    
    concatenated = Concatenate()([flattened1, flattened2])
    dropout = Dropout(dropout_rate)(concatenated)
    output = Dense(hidden_units, activation='relu')(dropout)
    output = Dense(1, activation='sigmoid')(output)
    
    model = Model(inputs=[input1, input2], outputs=output)
    optimizer = Adam(lr=0.001)
    model.compile(loss='binary_crossentropy', optimizer=optimizer, metrics=['accuracy'])
    
    model.fit([train_data1, train_data2], train_similarity, epochs=20, batch_size=32)
    
    modelo_entrenado.append((model, tokenizer, train_data1, train_data2)) 

def calcular_similitud( text1, text2):
    model, tokenizer, train_data1, train_data2 = modelo_entrenado[0] 
    text1_sequence = tokenizer.texts_to_sequences([text1])
    text2_sequence = tokenizer.texts_to_sequences([text2])
    text1_data = pad_sequences(text1_sequence, maxlen=train_data1.shape[1])
    text2_data = pad_sequences(text2_sequence, maxlen=train_data2.shape[1])
    
    similarity = model.predict([text1_data, text2_data])[0][0]
    return similarity

