import json , io, base64
import numpy as np
import matplotlib.pyplot as plt
import psycopg2
import pandas as pd
from sklearn import preprocessing
from sklearn import cluster , metrics
from sklearn.cluster import DBSCAN
from matplotlib import pyplot as plt
from sklearn.neighbors import NearestNeighbors

conn= psycopg2.connect(database="delati", user="modulo4", password="modulo4", host="128.199.1.222", port="5432")


def get_dataFrame(sql, conn):
    df = pd.read_sql(sql, con = conn)
    return df

def transform_data(dat):
    label_encoder = preprocessing.LabelEncoder()
    transformed_data = dat.apply(label_encoder.fit_transform)
    return transformed_data


def metodo_codo(dataTransformed):
    # Usamos vecinos más cercanos para calcular la distancia entre puntos.
    # calcular distancias 
    neigh=NearestNeighbors(n_neighbors=2)
    distance=neigh.fit(dataTransformed)
    # índices y valores de distancia
    distances,indices=distance.kneighbors(dataTransformed)
    # Ahora ordenando el orden creciente de distancia
    sorting_distances=np.sort(distances,axis=0)
    # distancias ordenadas
    sorted_distances=sorting_distances[:,1]
    return sorted_distances

def show_codo(data):
    codo=metodo_codo(data)
    #grafico entre distancia vs épsilon
    plt.plot(codo)
    plt.xlabel('Distancia')
    plt.ylabel('Epsilon')
    plt.title("GRÁFICO MÉTODO DEL CODO")
    plt.grid(color='grey', linestyle='-', linewidth=0.25, alpha=0.6)
    #plt.show()

    codo_image = io.BytesIO()
    plt.savefig(codo_image, format='jpg')
    codo_image.seek(0)
    codo_image_decode = base64.b64encode(codo_image.read())

    return codo_image_decode.decode()

def dbscan_model(eps, min_samples, query):
    result = {}
    #TODO: Obtener data desde la query
    data=get_dataFrame(query, conn)
    #TODO: transformamos la data
    dataTransformed = transform_data(data)
    # inicializamos DBSCAN
    clustering_model=DBSCAN(eps=eps,min_samples=min_samples)
    # ajustamos el modelo a transform_data
    clustering_model.fit_predict(dataTransformed)
    predicted_labels=clustering_model.labels_

    data['cluster'] = predicted_labels

    ########metrics and number of clusters####################
    n_clusters_ = len(set(predicted_labels)) - (1 if -1 in predicted_labels else 0)
    n_noise_    = list(predicted_labels).count(-1)
    coefficient = metrics.silhouette_score(dataTransformed, predicted_labels)

    clusters_uniques = set(list(predicted_labels))
    cant = list(predicted_labels)
    metricas_totales = []
    cantidad_cluster = {}
    for item in clusters_uniques:
        cantidad_cluster = {
            "clusters": int(item),
            "cantidad": cant.count(int(item)),
            "porcentaje": float(cant.count(int(item))/len(cant))   
                 }
        metricas_totales.append(cantidad_cluster)

    result['data'] = json.loads(data.to_json(orient = 'records'))
    result['metricas'] = { 
                'n_clusters': n_clusters_,
                'n_noise': n_noise_,
                'Coefficient': coefficient
                 }

    ##############visualizacion de DBSCAN ##################
#visualzing clusters

    dataTransformed['cluster']=predicted_labels

    clusters = dataTransformed['cluster'].apply(lambda x: 'cluster ' +str(x+1) if x != -1 else 'outlier')
    numero_clusters= len(set(clusters))
    print(numero_clusters)
    XX=dataTransformed.iloc[:,[0,1]].values

    plt.figure(figsize=(13,10))
    for i in range(numero_clusters):
        if (i-1) != -1:
            plt.scatter(XX[predicted_labels== (i-1), 0], XX[predicted_labels==(i-1), 1], s=80, cmap='Paired', label = clusters.unique())
        else:
            plt.scatter(XX[predicted_labels== (i-1), 0], XX[predicted_labels==(i-1), 1], s=80, c='Grey', label = clusters.unique())

    plt.legend(clusters.unique(),bbox_to_anchor=(0.99,1),fontsize=12)
    plt.grid(color='grey', linestyle='-', linewidth=0.25, alpha=0.6)
    plt.xlabel('Categoria')
    plt.ylabel('Datos')
    plt.title("DBSCAN")
    #plt.show()
 
    ##############
    
    my_stringIObytes = io.BytesIO()
    plt.savefig(my_stringIObytes, format='jpg')
    # plt.savefig("graphic2.jpg")
    my_stringIObytes.seek(0)
    my_base64_jpgData = base64.b64encode(my_stringIObytes.read())
    result["graphic_dbscan"] = my_base64_jpgData.decode()

    plt.figure(clear=True) 
    result["graphic_method_codo"] = show_codo(dataTransformed)

    result["numColumn"] = list(data.columns.values)

    result["metricas_detalles"] = metricas_totales

    

    return result





