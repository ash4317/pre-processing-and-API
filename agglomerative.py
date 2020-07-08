'''
Performs Agglomerative clustering
'''

# Modules imported
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from sklearn import metrics
from sklearn.cluster import AgglomerativeClustering
import extract as ex


def agglomerative_clustering(k, tfidf, isin_list, urllist):
    '''
    Performs agglomerative clustering
    '''
    agg = AgglomerativeClustering(n_clusters=k)
    agglo = agg.fit(tfidf)
    clusters = agglo.labels_.tolist()
    clustered_data={'ISIN':isin_list, 'URL':urllist,'Cluster':clusters} #Creating dict having url with the corresponding cluster number.
    frame=pd.DataFrame(clustered_data, columns=['ISIN','URL','Cluster']) # Converting it into a dataframe.

    sil = metrics.silhouette_score(tfidf, agglo.labels_)
    cal= metrics.calinski_harabasz_score(tfidf, agglo.labels_)
    db = metrics.davies_bouldin_score(tfidf, agglo.labels_)
    scores = [sil, cal, db]
    '''
    print(f"Silhouette score: {sil}")
    print(f"Calinski Harabasz score: {cal}")
    print(f"Davies Bouldin score: {db}")
    print("\n")
    '''
    return frame, scores


def visualize_scatter(k, tfidf):
    '''
    Plots scatter plot for clustering
    '''
    agg = AgglomerativeClustering(n_clusters=k)    
    y_agglo = agg.fit_predict(tfidf)
    fig = plt.figure()
    plt.scatter(tfidf[:, 0], tfidf[:, 1], c=y_agglo, s=50, cmap='viridis')
    plt.title("Agglomerative", figure=fig)
    return fig